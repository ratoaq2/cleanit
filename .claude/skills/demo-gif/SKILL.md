---
name: demo-gif
description: Record the README terminal demo docs/images/demo.gif with VHS in a container. Use to make or update the demo GIF.
---

# Demo GIF

`docs/images/demo.gif` shows a cleanit session in a terminal. VHS records it in a container:

- `scripts/demo/movie.en.srt`: the sample file. It is written by hand. Each entry shows one rule tag.
- `scripts/demo.tape`: the session that VHS types and records. It is the source of the current GIF.
- `scripts/demo.Dockerfile`: the cleanit image, plus VHS, ttyd, and Chromium.
- `scripts/demo.sh`: builds the cleanit image and the VHS image, mounts the repository, and records.

The tape copies the sample to `/demo` in the container and cleans the copy. The sample in the repository
does not change.

## 1. Edit

- To show other changes, edit `scripts/demo/movie.en.srt`. Use invented text, not text from a real movie.
  Check the result on the host first:

  ```
  cp scripts/demo/movie.en.srt <scratchpad>/
  uv run cleanit -t default --test --debug <scratchpad>/movie.en.srt
  ```

- To change the commands, edit `scripts/demo.tape`. Keep the hidden setup at the top. It goes to `/demo`
  and sets the prompt to `$ `. The GIF must not show a path.

## 2. Record

1. On Windows or macOS, start the Podman machine: `podman machine start`. It is not an error if it runs
   already.
2. From the repository root, run `bash scripts/demo.sh`. The first build takes some minutes.

Known problems that the scripts already solve:

- Debian has no `ttyd` package. `scripts/demo.Dockerfile` downloads the static binary.
- Git Bash changes `/repo` into a Windows path. `scripts/demo.sh` sets `MSYS_NO_PATHCONV=1`.
- Podman on WSL fails with "controller `pids` is not available". `scripts/demo.sh` adds
  `--cgroups=disabled` for Podman.
- At a width of 900, the progress bar wraps, and a letter of the file name stays before the next prompt.
  Keep `Set Width 1100`.
- At the default frame rate (50), VHS drops frames in the container, and the GIF plays too fast.
  `Set Framerate 10` keeps the real time. The GIF duration must be about the sum of the `Sleep` and the
  typing time.

## 3. Check the frames

Save some frames as PNG, then read them:

```
uv run --no-project --with pillow python -c "
from PIL import Image
im = Image.open('docs/images/demo.gif')
n = im.n_frames
print(im.size, n, 'frames', sum((im.seek(i), im.info.get('duration', 0))[1] for i in range(n)) / 1000, 's')
for k, f in enumerate([n * 6 // 10, n - 1]):
    im.seek(f)
    im.convert('RGB').save(f'<scratchpad>/frame{k}.png')
"
```

Look for these problems:

- The first `cat` is not complete in the last frame: increase `Set Height` in the tape.
- A large empty area at the bottom of the last frame: decrease `Set Height`.
- A character stays before a prompt: see the width problem above.
- The GIF is more than about 2 MB or 25 s: make the sample shorter.

## 4. Finish

1. Show the frames to the user, with the size and the duration of the GIF.
2. `README.md` shows `docs/images/demo.gif` with an absolute `raw.githubusercontent.com` URL, so that
   PyPI shows it too. Change its alt text if the demo changed.
3. To commit, use the `ship` skill. Commit `docs/images/demo.gif`, `scripts/demo.tape`, and the sample
   together.
