"""Preserve already rendered packets; assemble ABC and corrected prefix, never old fold."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import subprocess

P = Path(__file__).resolve().parent
R = P.parent
TEMP = Path('/tmp/s14_user_repair_20261020')

def run(args):
    result = subprocess.run(args, check=True, capture_output=True)
    if result.stderr:
        raise RuntimeError(result.stderr.decode())
    return result.stdout

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def framehash(video):
    content = run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(video),
                   '-an', '-f', 'framehash', '-hash', 'sha256', '-']).decode()
    values = [line.rsplit(',', 1)[-1].strip() for line in content.splitlines()
              if line and not line.startswith('#')]
    return content, values

def assemble(name, sources, count):
    final = P / name
    if final.exists():
        raise RuntimeError('Existing output preserved: ' + str(final))
    chunks = P / (final.stem + '_PACKET_SOURCES.txt')
    chunks.write_text(''.join("file '" + str(path) + "'\n" for path in sources))
    run(['ffmpeg', '-n', '-v', 'error', '-f', 'concat', '-safe', '0',
         '-i', str(chunks), '-c', 'copy', '-movflags', '+faststart', str(final)])
    probe = json.loads(run(['ffprobe', '-v', 'error', '-count_frames',
                           '-show_streams', '-show_format', '-of', 'json', str(final)]))
    assert len(probe['streams']) == 1
    video = probe['streams'][0]
    assert video['codec_type'] == 'video'
    assert int(video['nb_read_frames']) == count and video['r_frame_rate'] == '24/1'
    assert (video['width'], video['height']) == (1920, 1080)
    assert abs(float(probe['format']['duration']) - count / 24) < 0.000002
    expected = []
    for path in sources:
        expected.extend(framehash(path)[1])
    decoded, actual = framehash(final)
    assert actual == expected and len(actual) == count
    (P / (final.stem + '_DECODE_FRAMEHASH.txt')).write_text(decoded)
    return {'file': str(final.relative_to(R)), 'sha256': sha(final),
            'bytes': final.stat().st_size, 'frames': count,
            'fps': 24, 'seconds': count / 24, 'width': 1920, 'height': 1080,
            'audioStreams': 0, 'decodedPacketsPreserved': True,
            'sourceMP4s': [{'path': str(path.relative_to(R)), 'sha256': sha(path)}
                           for path in sources]}

actual = P / 'actual_C162_196'
if actual.exists():
    raise RuntimeError('Existing C delivery retained; no automatic retry')
actual.mkdir()
for source, label, frames in [
    (TEMP / 'actual_C162_195_34frames', 'C162_195', list(range(162, 196))),
    (TEMP / 'actual_C_boundary196_once', 'C196_ONCE', [196])
]:
    log = json.loads((source / 'EXECUTION_LOG.json').read_text())
    assert log['status'] == 'TECHNICAL_COMPLETE_PENDING_ACTUAL_VISUAL_REVIEW'
    assert log['requestedFrames'] == frames
    assert [row['frame'] for row in log['renderedFrames']] == frames
    assert not log['requestFailures'] and not log['pageErrors']
    assert all(row['sourceSHA256'] == 'c046100d91b59b40715747df93c4dda01f19f123246f8c9baa0de8aab5e71209'
               and not row['diagnosticExposureOnly'] for row in log['renderedFrames'])
    for path in source.iterdir():
        name = path.name if path.suffix == '.png' else label + '_' + path.name
        shutil.copy2(path, actual / name)
        assert sha(path) == sha(actual / name)

c = assemble('S14_NEW_C_162_196_35F.mp4',
             [actual / 'C162_195_S14_ACTUAL_SEGMENT.mp4',
              actual / 'C196_ONCE_S14_ACTUAL_SEGMENT.mp4'], 35)
abc = assemble('S14_EXISTING_DRAG_A_B_C_132_196_65F.mp4',
               [P / 'S14_EXISTING_DRAG_A_B_132_161_30F.mp4', P / 'S14_NEW_C_162_196_35F.mp4'], 65)
prefix = assemble('S14_REPAIRED_GRANDMA_PREFIX_000_131_132F.mp4',
                  [P / 'S14_GRANDMA_000_095_4S_CANDIDATE.mp4',
                   R / 'actual_close096_131/S14_ACTUAL_SEGMENT.mp4'], 132)
record = {
    'status': 'ACTUAL_ABC_PARTIAL_COMPLETE_OLD_FOLD_REJECTED_PENDING_C_MOTHER_ARM_ART',
    'createdUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'C': c, 'ABC': abc, 'correctedPrefix': prefix,
    'newSceneRenderedFramesForC': 35, 'rerenderedC196': False,
    'extraSceneRendersForAssembly': 0, 'imageGenerationCalls': 0,
    'sourceCCommit': '587ea678b2f27218710dd6cec07e551d1a16754c',
    'sourceCSHA256': 'c046100d91b59b40715747df93c4dda01f19f123246f8c9baa0de8aab5e71209',
    'rawRegistrationAppliedAgain': False,
    'naturalShortCalvesAndHangingFeetPreserved': True,
    'seatedDownwardNodSourcesConsumed': False,
    'oldLongBody197To239Consumed': False,
    'remainingArt': 'Two complete figures derived from C mother: arms collecting at chest197–202; crossed arms203–239. Same head, torso, hip, short legs and hanging shoes.',
    'wholeS14DurationSeconds': 10, 'wholeRepairAccepted': False
}
(actual / 'C_ACTUAL_PARTIAL_DELIVERY.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(record, ensure_ascii=False))
