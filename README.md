# Digital Beaver Apps

The latest versions of Digital Beaver's Android apps, with download links and what's new:
**https://stevebodyjr.github.io/apps/**

It's an installable web app (PWA): on Android Chrome, use **Install** on the page (or the browser
menu → Add to home screen). It opens offline and shows the last list it saw.

## Publishing a new version

```
py tools/publish.py until 1.3.0 "C:/Users/user/Downloads/My APKs/Until/Until-v1.3.0.apk" --note "What's new." --note "Another change."
```

This uploads the APK as a release of this repo, adds it to `releases.json`, commits and pushes.
App ids: `until`, `hdstatus`, `futureme`, `folio`, `passwordvault`, `mylibrary`. A new app needs an entry in `releases.json` first
(id, name, icon in `icons/`, tagline, package, minAndroid).

## Files

| File | What |
| --- | --- |
| `index.html` | The page (reads `releases.json`) |
| `releases.json` | Apps, versions, notes; downloads point to this repo's releases |
| `sw.js` | Offline cache (page from cache, list from the network first) |
| `manifest.webmanifest`, `icons/` | Installable app name and icons |

APKs are only stored as release assets, never committed. The apps' source code lives in private repos.
