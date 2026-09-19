---
title: "Porting C & SDL2 Games to the Web using Emscripten and WebAssembly"
date: "2026-08-28"
readTime: "8 min read"
tags: ["C", "SDL2", "WebAssembly", "Emscripten"]
excerpt: "A practical guide to taking desktop C code written with SDL2 and compiling it to high-performance Wasm running natively in any modern browser."
---

WebAssembly (Wasm) has bridged the gap between native systems programming and the open web. Using Emscripten (`emcc`), we can compile a C99 codebase utilizing Simple DirectMedia Layer (SDL2) directly into an HTML5 Canvas-compatible bundle.

## The Emscripten Loop

In desktop C/SDL2, game loops typically use a blocking `while (running)` loop. In browser environments, this would freeze the JavaScript UI thread. 

Emscripten provides `emscripten_set_main_loop` to schedule ticks cooperatively with the browser's `requestAnimationFrame`:

```c
#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif

void main_loop(void) {
    handle_events();
    update_game_state();
    render_frame();
}

int main(int argc, char* argv[]) {
    init_sdl();
#ifdef __EMSCRIPTEN__
    emscripten_set_main_loop(main_loop, 0, 1);
#else
    while (running) main_loop();
#endif
    return 0;
}
```

## Compilation Command

To compile your C game using Emscripten:

```bash
emcc src/main.c -O3 -s USE_SDL=2 -s USE_SDL_IMAGE=2 -s WASM=1 -o game.html
```

The resulting `.wasm` file runs at near-native speeds directly in modern Chromium, Firefox, and WebKit engines without any plugins.
