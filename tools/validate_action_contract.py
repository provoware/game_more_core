#!/usr/bin/env python3
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'manifests/ACTION_MANIFEST.json').read_text(encoding='utf-8'))
skill_manifest = json.loads((ROOT / 'manifests/SKILL_MANIFEST.json').read_text(encoding='utf-8'))
trait_manifest = json.loads((ROOT / 'manifests/TRAIT_ENGINE_MANIFEST.json').read_text(encoding='utf-8'))
journal = json.loads((ROOT / 'manifests/JOURNAL_MANIFEST.json').read_text(encoding='utf-8'))
skills = {x['skill_id'].split('.',1)[1] for x in skill_manifest['skills']}
traits = {x['effect_template_id'].split('.',1)[1] for x in trait_manifest['effect_templates']}
events = set(journal['event_types'])
ids = set()
for action in manifest['actions']:
    aid = action['action_id']
    assert aid not in ids, f'doppelte Action-ID: {aid}'
    ids.add(aid)
    assert abs(sum(action['skill_weights'].values()) - 1.0) < 1e-9, f'Skill-Gewichte != 1: {aid}'
    assert abs(sum(action['trait_evidence_weights'].values()) - 1.0) < 1e-9, f'Trait-Gewichte != 1: {aid}'
    for key in action['skill_weights']:
        assert key in skills or key == 'selected_skill', f'unbekannter Skill {key}: {aid}'
    for key in action['trait_evidence_weights']:
        assert key in traits or key == 'selected_trait_family', f'unbekannte Trait-Familie {key}: {aid}'
    for event in action['journal_events']:
        assert event in events, f'unbekannter Journaltyp {event}: {aid}'
    assert 0 <= action['biography_importance_base'] <= 100
assert len(manifest['actions']) == 20
print('ACTION_CONTRACT PASS: 20 Actions, Gewichte/Referenzen/Journaltypen gültig')
