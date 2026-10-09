#!/usr/bin/env python3
"""Read-only integrity check for the current draft wrapper; no runtime claims."""
from pathlib import Path
import json, hashlib, re, subprocess, sys
root = Path(__file__).resolve().parents[3]
package = root / 'patches/vlc-master/feature-series'
candidate = root / 'work/upstream/vlc-master-story005-candidate'
manifest = json.loads((package / 'manifest.json').read_text())
validation = json.loads((root / 'docs/evidence/story-005/public-feature-series-validation.json').read_text())
sha = lambda data: hashlib.sha256(data).hexdigest()
def contained_file(directory, name):
    path = (directory / name).resolve()
    assert path.is_relative_to(directory.resolve()) and path.is_file(), name
    return path

assert sha((package / 'manifest.json').read_bytes()) == validation['manifest_sha256']
assert manifest['candidate_source_tree'] == validation['source_tree']
assert manifest['base'] == validation['base']
assert manifest['revision'] == validation['revision']
assert len(manifest['files']) == manifest['source_file_count'] == 59
assert len({entry['path'] for entry in manifest['files']}) == len(manifest['files'])
assert sum(entry['bytes'] for entry in manifest['files']) == manifest['source_bytes'] == validation['source_tree_byte_count']
for entry in manifest['files']:
    source = contained_file(candidate, entry['path'])
    data = source.read_bytes()
    assert sha(data) == entry['sha256'] and len(data) == entry['bytes'], entry['path']
    assert entry['git_mode'] == ('100755' if source.stat().st_mode & 0o111 else '100644'), entry['path']
    assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == entry['git_blob'], entry['path']
assert len(manifest['series']) in (4, 5)
for group in [manifest['series'], manifest['review_artifacts'], validation['artifact_files']]:
    assert len({entry['file'] for entry in group}) == len(group)
    for entry in group:
        data = contained_file(package, entry['file']).read_bytes()
        assert sha(data) == entry['sha256'] and len(data) == entry['bytes'], entry['file']
actual_files = {str(file.relative_to(package)) for file in package.rglob('*') if file.is_file()}
assert actual_files == {entry['file'] for entry in validation['artifact_files']}
assert actual_files == {'manifest.json'} | {entry['file'] for entry in manifest['series']} | {entry['file'] for entry in manifest['review_artifacts']}
assert 'LIMITATIONS.md' in {entry['file'] for entry in manifest['review_artifacts']}
assert (package / 'series').read_text().splitlines() == [e['file'] for e in manifest['series']]
assert manifest['validation']['steps'] == validation['applications']
assert [entry['patch'] for entry in validation['applications']] == [entry['file'] for entry in manifest['series']]
assert all(entry['apply_check'] == entry['apply'] == 'pass' for entry in validation['applications'])
assert validation['applications'][-1]['tree'] == manifest['validation']['resulting_tree'] == validation['source_tree']
assert manifest['validation']['exact_source_tree_match'] is True and validation['exact_source_tree_match'] is True
assert validation['source_indexes_before'] == validation['source_indexes_after']
assert sum(entry['bytes'] for entry in manifest['series']) == validation['patch_bytes']
assert sum(f.stat().st_size for f in package.rglob('*') if f.is_file()) == validation['artifact_bytes']
assert validation['conservative_peak_with_final_metadata_bytes'] < 20 * 1024 * 1024
patterns = [r'/Users/', r'/Volumes/', r'smb://', r'work/story', r'-----BEGIN .*PRIVATE KEY', r'sk-proj-[A-Za-z0-9_-]{20,}', r'\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2[0-9]|3[01])(?:\.\d{1,3}){2})\b']
for file in package.rglob('*'):
    if not file.is_file():
        continue
    data = file.read_bytes()
    text = data.decode('latin1') if file.suffix == '.png' else data.decode('utf8')
    if file.suffix != '.png':
        assert '\0' not in text
    else:
        assert data.startswith(b'\x89PNG\r\n\x1a\n') and data.endswith(b'IEND\xaeB`\x82')
    for pattern in patterns:
        assert not re.search(pattern, text), (file.name, pattern)
    if file.suffix == '.md':
        assert 'confirmed by' not in text and 'approved contributor/contact credit as' not in text
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if not re.match(r'\w+://', target):
                linked = (file.parent / target).resolve()
                assert linked.is_relative_to(package.resolve()) and linked.is_file(), (file.name, target)
attribution = manifest['shutdown_baseline_attribution']
assert attribution['file'] == 'LIMITATIONS.md'
attribution_file = contained_file(package, attribution['file'])
attribution_data = attribution_file.read_bytes()
assert sha(attribution_data) == attribution['sha256'] and len(attribution_data) == attribution['bytes']
for pattern in patterns:
    assert not re.search(pattern, attribution_data.decode('utf8')), ('shutdown attribution', pattern)
for target in re.findall(r'\]\(([^)]+)\)', attribution_data.decode('utf8')):
    if not re.match(r'\w+://', target):
        linked = (attribution_file.parent / target).resolve()
        assert linked.is_relative_to(package.resolve()) and linked.is_file()
assert len(attribution['unchanged_sources']) == 8
assert len({entry['path'] for entry in attribution['unchanged_sources']}) == 8
for entry in attribution['unchanged_sources']:
    baseline_data = (root / 'work/upstream/vlc-master-story005' / entry['path']).read_bytes()
    assert sha(baseline_data) == entry['sha256']
    assert baseline_data == (candidate / entry['path']).read_bytes()
assert manifest['status'].startswith('Prepared for maintainer review; submission checklist incomplete')
assert 'demonstration/README.md' in (package / 'contribution-description-draft.md').read_text()
demo = json.loads((package / 'demonstration/provenance.json').read_text())
originals = {'custom-fullscreen-hover.png': root / 'work/story005-native-baseline/candidate007-custom/custom-fullscreen-hover.png', 'detached-hover.png': root / 'work/story005-native-baseline/candidate007-detached/detached-hover.png'}
for entry in demo['screenshots']:
    source = originals[entry['file']].read_bytes()
    copied = (package / 'demonstration' / entry['file']).read_bytes()
    assert copied == source
    assert sha(source) == entry['sha256'] == entry['original_sha256']
assert sha((root / 'work/story005-public-long001/long-preparation.mp4').read_bytes()) == demo['fixture']['sha256']
assert 'not a recording' in (package / 'demonstration/README.md').read_text()
identity_scope = 'fresh Git identity'
if '--reuse-verified-identity' in sys.argv:
    prior = json.loads((root / 'work/story005-final-wrapper-before/manifest.json').read_text())
    for key in ('name', 'email'):
        assert prior['contributor_guidance'][key] == manifest['contributor_guidance'][key]
    prior_result = json.loads((root / 'docs/evidence/story-005/native-outcome-wrapper-update-001.log').read_text())
    assert prior_result['status'] == 'passed'
    assert prior_result['manifest_sha256'] == sha((root / 'work/story005-final-wrapper-before/manifest.json').read_bytes())
    identity_scope = 'prior passing identity explicitly reused; no fresh Git query'
else:
    for field, key in [('user.name', 'name'), ('user.email', 'email')]:
        assert subprocess.check_output(['git', '-C', str(root), 'config', field], timeout=5).decode().strip() == manifest['contributor_guidance'][key]
previous_package = root / 'work/story005-review-baseline010/patches/vlc-master/feature-series'
previous = json.loads((previous_package / 'manifest.json').read_text())
previous_demo = json.loads((previous_package / 'demonstration/provenance.json').read_text())
for key in ('screenshots', 'production_build_tree', 'source_series_tree', 'isolation', 'fixture'):
    assert demo[key] == previous_demo[key], ('historical demonstration', key)
previous_series = {entry['file']: entry for entry in previous['series']}
current_series = {entry['file']: entry for entry in manifest['series']}
for name in ('0000-source-header-distribution.patch', '0001-contrib-matroska-identity-and-admission.patch'):
    assert current_series[name]['sha256'] == previous_series[name]['sha256']
    assert (package / name).read_bytes() == (previous_package / name).read_bytes()
print(json.dumps({'status': 'passed', 'checks': ['59 frozen source hashes/sizes/modes/blobs', str(len(validation['artifact_files'])) + ' exact artifact filenames/hashes/sizes', 'series order and recorded independent application/tree proof consistency', 'package-contained wrapper links', 'complete artifact private/binary marker scan', 'Git identity and approval precision', 'two PNG copies/source hashes and public fixture hash; historical runtime scope', '20MiB recorded storage cap', '0000/0001 revision10 lineage unchanged', 'package-contained shutdown attribution hash/privacy/links and eight unchanged source pins'], 'identity_scope': identity_scope, 'source_tree': manifest['candidate_source_tree'], 'manifest_sha256': validation['manifest_sha256'], 'artifact_bytes': validation['artifact_bytes'], 'artifact_files': validation['artifact_files']}, indent=2))
