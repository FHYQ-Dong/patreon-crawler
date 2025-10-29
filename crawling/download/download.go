package download

import (
	"fmt"
	"io"
	"iter"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"

	"patreon-crawler/patreon"
)

func GetMediaFile(downloadDirectory string, media patreon.Media) (string, error) {
	extension, err := getFileExtension(media.MimeType)
	if err != nil {
		return "", err
	}
	return fmt.Sprintf("%s/%s.%s", downloadDirectory, media.ID, extension), nil
}

func getFileExtension(mimeType string) (string, error) {
	// This is a very quick and dirty method, but it should work here
	mimeTypeSplits := strings.Split(mimeType, "/")
	if len(mimeTypeSplits) != 2 {
		return "", fmt.Errorf("invalid mime type: %s", mimeType)
	}
	return mimeTypeSplits[1], nil
}

func downloadMedia(media patreon.Media, downloadDir string) ReportItem {
	downloadedFilePath, err := GetMediaFile(downloadDir, media)
	if err != nil {
		return NewErrorItem(media, err)
	}

	_, err = os.Stat(downloadedFilePath)
	if err == nil {
		return NewSkippedItem(media, "already downloaded")
	}

	response, err := http.Get(media.DownloadURL)
	if err != nil {
		return NewErrorItem(media, err)
	}
	defer response.Body.Close()

	if response.StatusCode != http.StatusOK {
		return NewErrorItem(media, fmt.Errorf("unexpected status code: %s", response.Status))
	}

	tempDownloadFilePath := downloadedFilePath + ".tmp"

	out, err := os.Create(tempDownloadFilePath)
	if err != nil {
		return NewErrorItem(media, fmt.Errorf("failed to create file: %w", err))
	}
	defer out.Close()

	_, err = io.Copy(out, response.Body)
	if err != nil {
		return NewErrorItem(media, fmt.Errorf("failed to write file: %w", err))
	}

	out.Close()

	err = os.Rename(tempDownloadFilePath, downloadedFilePath)
	if err != nil {
		return NewErrorItem(media, fmt.Errorf("failed to rename file: %w", err))
	}

	return NewSuccessItem(media)
}

func Post(downloadDirectory string, post patreon.Post) iter.Seq[ReportItem] {
	return func(yield func(ReportItem) bool) {
		if len(post.Media) == 0 {
			return
		}

		// Concurrency: default 8, can be overridden by environment variable
		concurrency := 8
		if v := os.Getenv("PATREON_CRAWLER_MEDIA_CONCURRENCY"); v != "" {
			if n, err := strconv.Atoi(v); err == nil && n > 0 {
				concurrency = n
			}
		}
		if concurrency > len(post.Media) {
			concurrency = len(post.Media)
		}
		if concurrency <= 0 {
			concurrency = 1
		}

		results := make(chan ReportItem, concurrency)
		done := make(chan struct{})
		var wg sync.WaitGroup
		sem := make(chan struct{}, concurrency)

		// Spawn concurrent tasks
		go func() {
		loop:
			for _, m := range post.Media {
				select {
				case <-done:
					break loop
				default:
				}

				if m.MimeType == "" {
					item := NewSkippedItem(m, "no mime type")
					select {
					case results <- item:
					case <-done:
					}
					continue
				}

				sem <- struct{}{}
				wg.Add(1)
				media := m
				go func() {
					defer func() { <-sem; wg.Done() }()
					item := downloadMedia(media, downloadDirectory)
					select {
					case results <- item:
					case <-done:
					}
				}()
			}
			wg.Wait()
			close(results)
		}()

		// Consume results and yield
		for item := range results {
			if !yield(item) {
				close(done)
				for range results { // wait for all tasks to finish to avoid leaks
				}
				return
			}
		}
	}
}
