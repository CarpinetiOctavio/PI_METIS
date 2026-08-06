import { useEffect, useRef } from "react";
import * as THREE from "three";
import { prefersReducedMotion, readCssVar } from "./canvasUtils";

// Puerta de entrada únicamente (RootLayout, pathname === "/") — hermano de
// GridScanBackground, va DEBAJO (mismo z-index negativo). DECISIÓN 045
// había descartado Three.js para los fondos de Bloque B por costo de
// bundle; este componente es la excepción documentada en el addendum de
// esa decisión — acotada a una sola ruta vía carga diferida (React.lazy en
// RootLayout), así que ninguna pantalla autenticada paga el costo.
//
// 18 hilos, paleta de 5 tonos interpolados entre --acc y --acc2 (los dos
// acentos que el sistema de diseño ya define) — pedido explícito de
// verificación manual (05/08/2026): "que se vieran más líneas y de
// distintos colores", sin salirse de la paleta de la identidad
// "Instrumento".
const THREAD_COUNT = 18;
const POINTS_PER_THREAD = 64;
const PALETTE_STEPS = 5;

export function ThreadsBackground() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const scene = new THREE.Scene();
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 10);
    camera.position.z = 1;

    // WebGL no está garantizado — GPU deshabilitada, navegador viejo, o el
    // propio jsdom de la suite de tests (routes.navigation.test.tsx navega
    // de verdad a "/" y monta este componente). Sin esta guarda,
    // `new THREE.WebGLRenderer()` tira y rompe el render de toda la puerta
    // de entrada en vez de degradar a "sin fondo Threads, GridScanBackground
    // sigue andando encima".
    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    } catch {
      return;
    }
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
    container.appendChild(renderer.domElement);

    const accent = new THREE.Color(readCssVar("--acc", "#22d3ee"));
    const accent2 = new THREE.Color(readCssVar("--acc2", "#c6f84e"));
    const palette: THREE.Color[] = [];
    for (let i = 0; i < PALETTE_STEPS; i++) {
      palette.push(accent.clone().lerp(accent2, i / (PALETTE_STEPS - 1)));
    }

    const lines: { line: THREE.Line; seed: number; yOffset: number; speed: number }[] = [];

    for (let i = 0; i < THREAD_COUNT; i++) {
      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array(POINTS_PER_THREAD * 3);
      geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
      const material = new THREE.LineBasicMaterial({
        color: palette[i % palette.length],
        transparent: true,
        opacity: 0.14 + (i / THREAD_COUNT) * 0.14,
      });
      const line = new THREE.Line(geometry, material);
      scene.add(line);
      lines.push({
        line,
        seed: Math.random() * 1000,
        yOffset: (i / (THREAD_COUNT - 1)) * 2 - 1,
        speed: 0.15 + Math.random() * 0.15,
      });
    }

    function resize() {
      const w = document.documentElement.clientWidth;
      const h = document.documentElement.clientHeight;
      renderer.setSize(w, h, false);
    }
    resize();
    window.addEventListener("resize", resize);

    // Mismas guardas que DotFieldBackground/GridScanBackground (B4, plan
    // pasada4 §4): sin esto, un rAF de WebGL corriendo en pestaña oculta o
    // fuera de viewport es el mismo desperdicio de CPU/batería que ya se
    // evitó para los otros dos fondos.
    let tabVisible = document.visibilityState === "visible";
    let inViewport = true;

    let rafId: number | null = null;
    function draw(t: number) {
      const time = t / 1000;
      for (const { line, seed, yOffset, speed } of lines) {
        const positions = line.geometry.attributes.position;
        for (let p = 0; p < POINTS_PER_THREAD; p++) {
          const x = (p / (POINTS_PER_THREAD - 1)) * 2 - 1;
          const wave =
            Math.sin(x * 3 + time * speed + seed) * 0.15 +
            Math.sin(x * 7 - time * speed * 1.7 + seed) * 0.05;
          positions.setXYZ(p, x, yOffset + wave, 0);
        }
        positions.needsUpdate = true;
      }
      renderer.render(scene, camera);
    }

    function loop(t: number) {
      if (tabVisible && inViewport) draw(t);
      rafId = requestAnimationFrame(loop);
    }

    if (prefersReducedMotion()) {
      draw(0);
    } else {
      rafId = requestAnimationFrame(loop);
    }

    function handleVisibilityChange() {
      tabVisible = document.visibilityState === "visible";
    }
    document.addEventListener("visibilitychange", handleVisibilityChange);

    const intersectionObserver = new IntersectionObserver(([entry]) => {
      inViewport = entry?.isIntersecting ?? true;
    });
    intersectionObserver.observe(container);

    return () => {
      if (rafId !== null) cancelAnimationFrame(rafId);
      window.removeEventListener("resize", resize);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      intersectionObserver.disconnect();
      for (const { line } of lines) {
        line.geometry.dispose();
        (line.material as THREE.Material).dispose();
      }
      renderer.dispose();
      container!.removeChild(renderer.domElement);
    };
  }, []);

  return (
    <div
      ref={containerRef}
      aria-hidden="true"
      style={{ position: "fixed", inset: 0, zIndex: -2, pointerEvents: "none" }}
    />
  );
}
