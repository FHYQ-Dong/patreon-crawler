Simple tool to download all media from a patreon creator using a chrome cookie file

## Usage

Requires Python 3.12 or higher.

```shell
python patreon_crawler.py --creator <creator1,creator2, ...> --cookie-file <path-to-chrome-cookie-file | 'auto'>
```

<br>

Use the interactive mode to set `creator` and `cookie-file` interactively by omitting the arguments.

```shell
python patreon_crawler.py
```

> **Note:** Chrome locks the cookie file while the browser is running. Make sure to close all chrome instances before running the script.

### Arguments

| Argument                 | Description                                                                                                                                                                                                                                                  |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `creator`                | A comma seperated list of all creators to crawl                                                                                                                                                                                                              |
| `cookie-file`            | The path to the chrome-cookie file to use for authentication. Use `auto` to try to determine the file automatically.                                                                                                                                         |
| `download-dir`           | The base directory to download media to. All files will be located in `<download-dir>/<creator>`. Defaults to `./downloads` if unset                                                                                                                         |
| `max-posts`              | The maximum number of posts to crawl.                                                                                                                                                                                                                        |
| `download-inaccessible`  | Whether to download media that is inaccessible (blurred images)                                                                                                                                                                                              |
| `max-parallel-downloads` | The maximum downloads to run in parallel                                                                                                                                                                                                                     |
| `post-grouping-strategy` | The strategy for grouping post media into folders. <br>`none` - Puts all media into the same folder (per creator)<br>`all` - Creates a folder for each post, containing its media <br>`dynamic` - Posts with more than one file are grouped into a directory |

