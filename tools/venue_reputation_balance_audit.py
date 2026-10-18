#!/usr/bin/env python3
"""Read-only proposal audit. This formula is NOT an active gameplay rule."""
from itertools import product
import json
from pathlib import Path

from bunkerfrequenz.domain.property_upgrade import MAX_UPGRADE_LEVEL, effective_venue_values

ROOT = Path(__file__).resolve().parents[1]


def proposed_bonus(audience_pull: int, reputation_delta: int, *, owned: bool) -> int:
    if isinstance(audience_pull, bool) or not isinstance(audience_pull, int) or not 0 <= audience_pull <= 100:
        raise ValueError('Publikumskraft muss eine Ganzzahl in 0..100 sein')
    if isinstance(reputation_delta, bool) or not isinstance(reputation_delta, int):
        raise ValueError('Rufdelta muss eine Ganzzahl sein')
    if not isinstance(owned, bool):
        raise ValueError('Besitzbestätigung muss bool sein')
    return min(2, audience_pull // 50, reputation_delta // 4) if owned and reputation_delta > 0 else 0


def run_audit() -> dict:
    cases = 0
    for owned in (False, True):
        for delta in range(-100, 101):
            previous = 0
            for audience in range(101):
                bonus = proposed_bonus(audience, delta, owned=owned)
                if not 0 <= bonus <= 2 or 4 * bonus > max(0, delta):
                    raise ValueError('Vorschlag verletzt absoluten oder relativen Bonus-Cap')
                if (not owned or delta <= 0) and bonus != 0:
                    raise ValueError('Vorschlag belohnt fehlenden Besitz oder erfolglose Events')
                if bonus < previous:
                    raise ValueError('Vorschlag ist nicht monoton in Publikumskraft')
                previous = bonus
                cases += 1

    # Check signed deltas outside the exhaustive envelope as well; the cap is independent of their magnitude.
    for delta in (-10**12, -101, 101, 10**12):
        for audience in range(101):
            bonus = proposed_bonus(audience, delta, owned=True)
            if bonus not in (0, 1, 2) or 4 * bonus > max(0, delta):
                raise ValueError('Vorschlag verletzt Cap außerhalb des Audit-Intervalls')

    city = json.loads((ROOT / 'manifests/CITY_MAP_MANIFEST.json').read_text())
    upgrades = json.loads((ROOT / 'manifests/PROPERTY_UPGRADE_MANIFEST.json').read_text())
    settlement = json.loads((ROOT / 'manifests/SETTLEMENT_MANIFEST.json').read_text())
    if 'venue_audience_pull' in settlement['application'] or 'audience_pull' in settlement['source_effects']:
        raise ValueError('Aktiver Wirkungsvertrag verändert: Auditentscheidung neu bewerten')
    venues = []
    for location in city['locations']:
        if not location.get('purchasable'):
            continue
        slots = location['upgrade_slots']
        reachable = set()
        combinations = 0
        for levels in product(range(MAX_UPGRADE_LEVEL + 1), repeat=len(slots)):
            values = effective_venue_values(location['values'], upgrade_slots=slots,
                                           upgrade_levels=dict(zip(slots, levels)),
                                           upgrade_catalog=upgrades['catalog'])
            reachable.add(values['audience_pull'])
            combinations += 1
        venues.append({'location_id': location['location_id'], 'upgrade_combinations': combinations,
                       'audience_min': min(reachable), 'audience_max': max(reachable),
                       'max_proposed_bonus_at_delta_8': proposed_bonus(max(reachable), 8, owned=True)})
    return {
        'decision': 'NO_GO_ACTIVATION_UNTIL_VERSIONED_EFFECT_CONTRACT_AND_PLAYTEST',
        'formula': 'owned and D > 0 ? min(2, A // 50, D // 4) : 0',
        'absolute_cap': 2, 'relative_cap_percent': 25,
        'exhaustive_cases': cases, 'audience_interval': [0, 100], 'reputation_delta_interval': [-100, 100],
        'extra_large_delta_cases': 404, 'money_effect': 0, 'runtime_mechanic_enabled': False,
        'retry_semantics': 'future effect must share the existing atomic, exactly-once event settlement',
        'venues': venues,
    }


if __name__ == '__main__':
    print(json.dumps(run_audit(), ensure_ascii=False, indent=2))
