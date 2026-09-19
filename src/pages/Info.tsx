import { User, GraduationCap, Briefcase, HardDrive, Code2, Layers, Terminal } from 'lucide-react';

export function Info() {
  return (
    <div className="space-y-10">
      {/* Header */}
      <div className="border-b border-zinc-800 pb-6">
        <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 mb-2">
          <User className="w-4 h-4" />
          <span>DEVELOPER PROFILE</span>
        </div>
        <h1 className="text-3xl font-bold text-zinc-100">About Me</h1>
        <p className="mt-2 text-zinc-400 text-sm sm:text-base">
          Background, academic journey at UFBA, work at TITAN, and computing philosophy.
        </p>
      </div>

      {/* Highlights Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Education */}
        <div className="border border-zinc-800 rounded-xl p-5 bg-zinc-900/40">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-3 border border-emerald-500/20">
            <GraduationCap className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-zinc-100 text-base">UFBA</h3>
          <p className="text-xs font-mono text-emerald-400 mt-0.5">Computer Science</p>
          <p className="text-xs text-zinc-400 mt-2">
            Currently in the <strong>4th semester</strong> of Computer Science (Ciência da Computação) at Universidade
            Federal da Bahia.
          </p>
        </div>

        {/* Junior Enterprise */}
        <div className="border border-zinc-800 rounded-xl p-5 bg-zinc-900/40">
          <div className="w-10 h-10 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center mb-3 border border-blue-500/20">
            <Briefcase className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-zinc-100 text-base">TITAN</h3>
          <p className="text-xs font-mono text-blue-400 mt-0.5">Backend Developer</p>
          <p className="text-xs text-zinc-400 mt-2">
            Member of <strong>TITAN</strong> (Empresa Júnior de Engenharia de Computação), building scalable backends,
            REST APIs, and database models.
          </p>
        </div>

        {/* Operating System */}
        <div className="border border-zinc-800 rounded-xl p-5 bg-zinc-900/40">
          <div className="w-10 h-10 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center mb-3 border border-purple-500/20">
            <HardDrive className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-zinc-100 text-base">Gentoo Linux</h3>
          <p className="text-xs font-mono text-purple-400 mt-0.5">Source-based OS</p>
          <p className="text-xs text-zinc-400 mt-2">
            Daily-driver operating system. Compiling from source, fine-tuning USE flags, custom kernel builds, and
            embracing Unix minimalism.
          </p>
        </div>
      </div>

      {/* Detailed Bio & Tech Stack */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Bio & Academic Focus */}
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-zinc-100 flex items-center gap-2">
            <Code2 className="w-5 h-5 text-emerald-400" /> Academic & Engineering Focus
          </h3>
          <div className="text-sm text-zinc-300 leading-relaxed space-y-3">
            <p>
              I am passionate about systems programming, backend architectures, and understanding software from
              the metal up to high-level network services.
            </p>
            <p>
              At <strong className="text-zinc-100">UFBA</strong>, my coursework in Computer Science covers data
              structures, algorithm analysis, computer architecture, and operating systems.
            </p>
            <p>
              At <strong className="text-zinc-100">TITAN</strong>, I work as a backend developer applying
              modern software engineering practices—delivering client-facing solutions with structured code,
              strong typings, and relational data modeling.
            </p>
          </div>
        </div>

        {/* Technical Stack */}
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-zinc-100 flex items-center gap-2">
            <Layers className="w-5 h-5 text-emerald-400" /> Technologies & Tools
          </h3>
          <div className="space-y-3">
            <div>
              <h4 className="text-xs font-mono text-zinc-400 uppercase tracking-wider mb-2">Systems & Languages</h4>
              <div className="flex flex-wrap gap-2">
                {['C (C99)', 'C++', 'TypeScript', 'JavaScript', 'Bash'].map((item) => (
                  <span key={item} className="px-2.5 py-1 rounded-md text-xs font-mono bg-zinc-900 border border-zinc-800 text-zinc-200">
                    {item}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-xs font-mono text-zinc-400 uppercase tracking-wider mb-2">Backend & Data</h4>
              <div className="flex flex-wrap gap-2">
                {['NestJS', 'Node.js', 'PostgreSQL', 'Prisma ORM', 'JWT', 'REST APIs'].map((item) => (
                  <span key={item} className="px-2.5 py-1 rounded-md text-xs font-mono bg-zinc-900 border border-zinc-800 text-zinc-200">
                    {item}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-xs font-mono text-zinc-400 uppercase tracking-wider mb-2">Gaming & Low-Level</h4>
              <div className="flex flex-wrap gap-2">
                {['SDL2', 'Emscripten', 'WebAssembly', 'Gentoo Linux', 'Portage'].map((item) => (
                  <span key={item} className="px-2.5 py-1 rounded-md text-xs font-mono bg-zinc-900 border border-zinc-800 text-zinc-200">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Gentoo Linux Highlight Box */}
      <div className="border border-emerald-500/20 bg-emerald-500/5 rounded-2xl p-6 sm:p-8">
        <div className="flex items-center gap-3 mb-4">
          <Terminal className="w-6 h-6 text-emerald-400" />
          <h3 className="text-lg font-bold text-zinc-100">Why Gentoo Linux?</h3>
        </div>
        <p className="text-sm text-zinc-300 leading-relaxed max-w-3xl">
          Gentoo provides unmatched transparency into how code translates into binaries. Configuring my kernel,
          managing dependencies through Portage, and eliminating unwanted bloat trains the discipline needed for
          writing high-performance backend systems and low-level C programs.
        </p>
      </div>
    </div>
  );
}
