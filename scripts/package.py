"""Monto uma entrega portátil, incluindo os arquivos que o Wokwi precisa."""
from pathlib import Path
import subprocess
import zipfile
ROOT = Path(__file__).resolve().parents[1]
firmware = ['build/flasher_args.json', 'build/har_esp32s3.bin', 'build/har_esp32s3.elf',
            'build/bootloader/bootloader.bin', 'build/partition_table/partition-table.bin',
            'build/merged-binary.bin']
for name in firmware:
    if not (ROOT / name).exists():
        raise SystemExit('Arquivo ausente: ' + name)
manifest = subprocess.run(
    ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
    cwd=ROOT, check=True, capture_output=True,
).stdout.decode('utf-8').split('\0')
# Respeito o .gitignore ao incluir fontes, documentação, modelo e resultados.
files = [ROOT / name for name in manifest if name and (ROOT / name).is_file()]
files.extend(ROOT / name for name in firmware)
# O pacote local é uma entrega pronta: pode levar as entradas e os binários.
# Esses arquivos derivados continuam fora do histórico Git.
test_header = ROOT / 'main/generated/test_data.h'
if test_header.exists():
    files.append(test_header)
target = ROOT / 'dist/entrega-har-esp32s3.zip'
target.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
    for p in sorted(set(files)):
        archive.write(p, 'ia-embarcada-projeto-final/' + p.relative_to(ROOT).as_posix())
print(f'Entrega: {target} ({target.stat().st_size:,} bytes)')
