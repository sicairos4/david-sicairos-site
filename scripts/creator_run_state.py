"""Opt-in local run checkpoints. No background execution or delivery."""
import hashlib
import json
import os
from pathlib import Path

from .creator_research_integration import write_handoff


class RunState:
    def __init__(self, root, identity):
        self.root = Path(root).expanduser()
        if not self.root.is_dir():
            raise ValueError('State directory must already exist in trusted private storage')
        encoded = json.dumps(identity, sort_keys=True, ensure_ascii=False).encode('utf-8')
        self.run_id = hashlib.sha256(encoded).hexdigest()
        self.directory = self.root / self.run_id
        self.lock = self.directory / 'RUNNING'
        self.owned = False

    def check_pause(self):
        if (self.root / 'PAUSED').exists() or (self.directory / 'PAUSED').exists():
            raise RuntimeError('Creator Engine is paused')

    def __enter__(self):
        self.check_pause()
        self.directory.mkdir(mode=0o700, exist_ok=True)
        if self.directory.is_symlink():
            raise ValueError('Run directory cannot be a symbolic link')
        try:
            descriptor = os.open(self.lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            raise RuntimeError('Run is locked; stale locks require deliberate owner removal') from None
        os.close(descriptor)
        self.owned = True
        return self

    def stage(self, name, producer):
        if name not in ('research', 'generation'):
            raise ValueError('Unsupported checkpoint stage')
        self.check_pause()
        target = self.directory / (name + '.json')
        if target.is_symlink():
            raise ValueError('Checkpoint cannot be a symbolic link')
        if target.exists():
            if target.stat().st_size > 8388608:
                raise ValueError('Checkpoint exceeds size limit')
            value = json.loads(target.read_text(encoding='utf-8'))
            if not isinstance(value, dict):
                raise ValueError('Checkpoint must contain an object')
            return value
        value = producer()
        if not isinstance(value, dict):
            raise ValueError('Stage must return an object')
        write_handoff(value, target)
        return value

    def __exit__(self, kind, value, traceback):
        if self.owned:
            self.lock.unlink(missing_ok=True)
            self.owned = False
        return False
