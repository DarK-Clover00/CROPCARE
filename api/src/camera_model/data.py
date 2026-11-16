import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random

import numpy as np
from PIL import Image, ImageOps
import torch
from torch.utils.data import Dataset
from torchvision import transforms

SIZE = 160

def read_image(path):
    with Image.open(path) as im:
        if im.width * im.height > 40_000_000:
            raise ValueError('Image exceeds 40 megapixels')
        return ImageOps.exif_transpose(im).convert('RGB')

def transform(train=False):
    steps = [transforms.Resize((SIZE, SIZE))]
    if train:
        steps += [transforms.RandomHorizontalFlip(), transforms.RandomVerticalFlip(),
                  transforms.RandomRotation(20), transforms.ColorJitter(.15, .15, .12, .03)]
    return transforms.Compose(steps + [transforms.ToTensor(), transforms.Normalize([.485, .456, .406], [.229, .224, .225])])

class Leaves(Dataset):
    def __init__(self, root, rows, classes, train=False):
        self.root, self.rows, self.classes = Path(root), rows, classes
        self.tf = transform(train)
    def __len__(self):
        return len(self.rows)
    def __getitem__(self, i):
        row = self.rows[i]
        return self.tf(read_image(self.root / row['path'])), self.classes.index(row['label'])

def prepare(root):
    root = Path(root)
    leaf_map = json.loads((root / 'leaf-map.json').read_text())
    rows, bad = [], []
    for path in sorted((root / 'raw').glob('*/*')):
        try:
            im = read_image(path)
            a = np.asarray(im.resize((9, 8)).convert('L'))
            dh = int(''.join(str(int(x)) for x in (a[:, 1:] > a[:, :-1]).flat), 2)
            key = path.name.replace('_final_masked', '').split('___')[-1].split('copy')[0]
            key = key.replace('.JPG', '').replace('.jpg', '').replace('.png', '').replace('.PNG', '').strip().lower()
            candidates = [x for x in leaf_map.get(key, []) if x.startswith(path.parent.name + ':::')]
            leaf = candidates[0] if len(candidates) == 1 else path.parent.name + '::fallback::' + key
            rows.append({'path': path.relative_to(root).as_posix(), 'label': path.parent.name,
                         'leaf': leaf, 'mapped_leaf': len(candidates) == 1, 'dhash': dh,
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        except Exception as e:
            bad.append({'path': str(path), 'error': str(e)})
    if not rows:
        raise ValueError('No valid images; run cropcare.download first')
    parent = list(range(len(rows)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    # Transitive components join leaf identities, exact duplicates and perceptual neighbors.
    for i, row in enumerate(rows):
        for j in range(i):
            other = rows[j]
            if row['leaf'] == other['leaf'] or row['sha256'] == other['sha256'] or (row['dhash'] ^ other['dhash']).bit_count() <= 4:
                parent[find(i)] = find(j)
    components = defaultdict(list)
    for i, row in enumerate(rows):
        components[find(i)].append(row)
    by_class = defaultdict(list)
    for group in components.values():
        if len({r['label'] for r in group}) != 1:
            bad.extend({'path': r['path'], 'error': 'Cross-label perceptual duplicate component excluded'} for r in group)
            continue
        by_class[group[0]['label']].append(group)
    splits = {'train': [], 'validation': [], 'test': []}
    rng = random.Random(42)
    for label, groups in sorted(by_class.items()):
        rng.shuffle(groups)
        if len(groups) < 10:
            raise ValueError(f'{label}: fewer than 10 independent groups')
        n = len(groups)
        for i, group in enumerate(groups):
            split = 'train' if i < int(n * .65) else 'validation' if i < int(n * .85) else 'test'
            for row in group:
                row['group'] = group[0]['sha256']
                splits[split].append(row)
    classes = sorted(by_class)
    manifest = {'classes': classes, 'splits': splits, 'seed': 42,
                'grouping': 'leaf-map + SHA256 + transitive dHash Hamming <=4',
                'counts': {s: dict(Counter(r['label'] for r in rr)) for s, rr in splits.items()},
                'excluded': bad, 'mapped_fraction': sum(r['mapped_leaf'] for r in rows) / len(rows)}
    (root / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    print(json.dumps({k: v for k, v in manifest.items() if k != 'splits'}, indent=2))
    return manifest

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='datasets')
    prepare(p.parse_args().root)
