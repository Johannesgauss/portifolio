import { useState } from 'react';
import { Gamepad2, Play, Code2, Maximize2, RotateCcw, Sparkles } from 'lucide-react';

export function Games() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [iframeKey, setIframeKey] = useState(0);

  const handleResetGame = () => {
    setIframeKey((prev) => prev + 1);
  };

  const handleFullscreen = () => {
    const iframe = document.getElementById('cetraminos-frame') as HTMLIFrameElement;
    if (iframe?.requestFullscreen) {
      iframe.requestFullscreen();
    }
  };

  return (
    <div className="space-y-10">
      {/* Page Header */}
      <div className="border-b border-zinc-800 pb-6">
        <div className="flex items-center gap-2 text-xs font-mono text-purple-400 mb-2">
          <Gamepad2 className="w-4 h-4" />
          <span>INTERACTIVE ARCADE / WEB ASSEMBLY</span>
        </div>
        <h1 className="text-3xl font-bold text-zinc-100">Games</h1>
        <p className="mt-2 text-zinc-400 text-sm sm:text-base">
          Native C & SDL2 games compiled to WebAssembly via Emscripten for zero-install, 60 FPS browser play.
        </p>
      </div>

      {/* Main Game Stage: Cetraminos */}
      <div className="border border-zinc-800 rounded-2xl bg-zinc-900/40 overflow-hidden shadow-2xl">
        {/* Game Canvas / IFrame Stage */}
        <div className="relative aspect-video max-h-[560px] w-full bg-zinc-950 flex flex-col items-center justify-center border-b border-zinc-800">
          {isPlaying ? (
            <iframe
              id="cetraminos-frame"
              key={iframeKey}
              src={`${import.meta.env.BASE_URL}games/cetraminos/index.html`}
              title="Cetraminos WebAssembly"
              className="w-full h-full border-0"
              allow="autoplay; fullscreen"
            />
          ) : (
            /* Splash / Ready Screen */
            <div className="p-8 text-center space-y-5 max-w-lg">
              <div className="w-16 h-16 rounded-2xl bg-purple-500/10 border border-purple-500/30 text-purple-400 flex items-center justify-center mx-auto shadow-lg shadow-purple-500/10">
                <Gamepad2 className="w-8 h-8" />
              </div>

              <div>
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-mono bg-purple-500/10 text-purple-300 border border-purple-500/20 mb-2">
                  <Sparkles className="w-3 h-3 text-purple-400" /> Featured C Game
                </span>
                <h2 className="text-2xl font-bold text-zinc-100 font-mono tracking-tight">Cetraminos</h2>
                <p className="text-xs sm:text-sm text-zinc-400 mt-2 leading-relaxed">
                  A custom Tetris-style arcade game built in pure C with SDL2. Features custom piece physics,
                  soundtrack audio with SDL2_mixer, and vector text with SDL2_ttf.
                </p>
              </div>

              <div className="pt-2">
                <button
                  onClick={() => setIsPlaying(true)}
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-xl font-mono text-sm font-semibold bg-purple-600 hover:bg-purple-500 text-white shadow-lg shadow-purple-600/30 transition-all cursor-pointer hover:scale-105 active:scale-95"
                >
                  <Play className="w-4 h-4 fill-white" /> Launch Cetraminos
                </button>
              </div>
            </div>
          )}

          {/* Interactive Screen Controls Bar (When Playing) */}
          {isPlaying && (
            <div className="absolute top-3 right-3 flex items-center gap-2 bg-zinc-900/90 backdrop-blur border border-zinc-700/60 p-1 rounded-lg">
              <button
                onClick={handleResetGame}
                title="Restart Frame"
                className="p-1.5 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 rounded transition-colors cursor-pointer"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              <button
                onClick={handleFullscreen}
                title="Fullscreen"
                className="p-1.5 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 rounded transition-colors cursor-pointer"
              >
                <Maximize2 className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Canvas Bottom Stats Bar */}
          <div className="absolute bottom-3 left-4 right-4 flex items-center justify-between text-[11px] font-mono text-zinc-500 pointer-events-none">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              HTML5 Canvas • SDL2 Accelerated
            </span>
            <span>Audio: Mix_Music • TTF Fonts</span>
          </div>
        </div>

        {/* Game Details, Controls & Technical Architecture */}
        <div className="p-6 sm:p-8 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                Cetraminos <span className="text-xs font-mono text-zinc-500 font-normal">v1.0</span>
              </h2>
              <p className="text-sm text-zinc-400 mt-1">
                Engineered with pure C99, compiled directly to WebAssembly using Emscripten.
              </p>
            </div>

            {/* Badges */}
            <div className="flex flex-wrap gap-1.5">
              {['C99', 'SDL2', 'SDL2_ttf', 'SDL2_mixer', 'WebAssembly', 'Emscripten'].map((tech) => (
                <span key={tech} className="px-2.5 py-1 rounded-md text-xs font-mono bg-zinc-800/80 text-zinc-300 border border-zinc-700/50">
                  {tech}
                </span>
              ))}
            </div>
          </div>

          {/* Keyboard Controls Section */}
          <div className="pt-4 border-t border-zinc-800/80">
            <div className="bg-zinc-950/70 p-5 rounded-xl border border-zinc-800/80">
              <h4 className="text-xs font-mono text-purple-400 font-semibold mb-4 flex items-center gap-1.5">
                <Code2 className="w-3.5 h-3.5" /> Keyboard Controls
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 text-xs font-mono text-zinc-300">
                <div className="flex flex-col justify-between gap-2 p-3 rounded-lg bg-zinc-900/60 border border-zinc-800/60">
                  <span className="text-zinc-400">Move</span>
                  <span className="self-start px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-200">← / →</span>
                </div>
                <div className="flex flex-col justify-between gap-2 p-3 rounded-lg bg-zinc-900/60 border border-zinc-800/60">
                  <span className="text-zinc-400">Spin / Rotate</span>
                  <span className="self-start px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-200">↑</span>
                </div>
                <div className="flex flex-col justify-between gap-2 p-3 rounded-lg bg-zinc-900/60 border border-zinc-800/60">
                  <span className="text-zinc-400">Soft Drop</span>
                  <span className="self-start px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-200">↓</span>
                </div>
                <div className="flex flex-col justify-between gap-2 p-3 rounded-lg bg-zinc-900/60 border border-zinc-800/60">
                  <span className="text-zinc-400">Hard Drop</span>
                  <span className="self-start px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-200">Left Ctrl</span>
                </div>
                <div className="flex flex-col justify-between gap-2 p-3 rounded-lg bg-zinc-900/60 border border-zinc-800/60">
                  <span className="text-zinc-400">Menu / Pause</span>
                  <span className="self-start px-2 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-200">ESC</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
