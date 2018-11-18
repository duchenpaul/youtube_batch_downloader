# Summary
Download youtube video as mp4 via proxy

# First use
Execute `database_deploy.py` to create a database

# Usage
1. make a list of youtube links naming it as `youtube_video.list`, e.g.
```
https://www.youtube.com/watch?v=bY6m6_IIN94
https://www.youtube.com/watch?v=f4KOjWS_KZs
```
2. `generate_download_list.py` to get the video link
3. `youtube_download.py` to download the video using proxy
4. If download fails, re-run `youtube_download.py`, the script will redownload failed videos