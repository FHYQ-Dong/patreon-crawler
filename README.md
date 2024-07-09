Simple tool to download all media from a patreon creator. Available on `win` only.

## Usage

```python
python patreon_crawler.py --creator < creator1, creator2, ... > --cookie - file < path - to - chrome - cookie - file > --download - dir < output - dir >
```

<br>

Use the interactive mode to set `creator` and `cookie-file` interactively by omitting the arguments.

```python
python patreon_crawler.py
```

### Arguments

| Argument       | Description                                                                                                           |
|----------------|-----------------------------------------------------------------------------------------------------------------------|
| `creator`      | A comma seperated list of all creators to crawl                                                                       |
| `cookie-file`  | The path to the chrome-cookie file to use for authentication. User `auto` to try to determine the file automatically. |
| `download-dir` | The base directory to download media to. All files will be locaed in `<download-dir>/<creator>`                       |

