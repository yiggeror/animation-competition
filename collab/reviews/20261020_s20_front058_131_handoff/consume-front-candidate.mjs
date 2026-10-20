// Existing-art resolver only. Never paints old rigs or fabricates missing mechanism.
export function resolveFrontState(table, frame, { enableCandidate = false } = {}) {
  if (!enableCandidate || !Number.isInteger(frame) || frame < 58 || frame > 131) return null;
  const hits = table.states.filter(s => frame >= s.candidateExposureInclusive[0] && frame <= s.candidateExposureInclusive[1]);
  if (hits.length !== 1) throw new Error(`S20 front coverage error at ${frame}`);
  return { ...hits[0], requestedFrame: frame, inputGuideIsNotFinalContact: true };
}
export function masterToCAM(table, p) {
  const a = table.peopleToCAM20;
  if (!Array.isArray(a) || a.length !== 6 || !a.every(Number.isFinite) || !p.every(Number.isFinite)) throw new Error('Invalid source CAM matrix');
  return [a[0]*p[0]+a[2]*p[1]+a[4],a[1]*p[0]+a[3]*p[1]+a[5]];
}
export async function loadVerifiedState(table, frame, { enableCandidate = false, loadBytes, sha256 } = {}) {
  const state = resolveFrontState(table, frame, { enableCandidate });
  if (!state) return null;
  if (typeof loadBytes !== 'function' || typeof sha256 !== 'function') throw new Error('Verified source byte loader required');
  const bytes = await loadBytes(state.path, state.sourceFetchCommit);
  if (await sha256(bytes) !== state.sha256) throw new Error(`Wrong adopted S20 PNG: ${state.frame}`);
  return { state, bytes }; // host supplies actual original scene/prop renderer, not a placeholder
}
