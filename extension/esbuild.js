const esbuild = require("esbuild");

const isProduction = process.argv.includes("--production");
const isWatch = process.argv.includes("--watch");

/**
 * VS Code problem matcher plugin
 * Shows TypeScript errors nicely in watch mode
 */
const esbuildProblemMatcherPlugin = {
  name: "esbuild-problem-matcher",
  setup(build) {
    build.onStart(() => {
      console.log("🔄 Build started...");
    });

    build.onEnd(result => {
      if (result.errors.length === 0) {
        console.log("✅ Build finished successfully");
      } else {
        console.log("❌ Build finished with errors");
        result.errors.forEach(error => {
          const loc = error.location;
          if (loc) {
            console.error(
              `✘ ${error.text}\n  at ${loc.file}:${loc.line}:${loc.column}`
            );
          } else {
            console.error(`✘ ${error.text}`);
          }
        });
      }
    });
  }
};

async function build() {
  const ctx = await esbuild.context({
    entryPoints: ["src/extension.ts"],
    bundle: true,
    platform: "node",
    format: "cjs",
    outfile: "dist/extension.js",
    sourcemap: !isProduction,
    minify: isProduction,
    external: ["vscode"],
    logLevel: "silent",
    plugins: [esbuildProblemMatcherPlugin]
  });

  if (isWatch) {
    await ctx.watch();
  } else {
    await ctx.rebuild();
    await ctx.dispose();
  }
}

build().catch(err => {
  console.error("❌ Build failed:", err);
  process.exit(1);
});
