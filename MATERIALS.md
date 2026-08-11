# Материалы проекта Deck Tracker Fix

Актуальное состояние зафиксировано 11 августа 2026 года после полного отката
неудачных экспериментов с вводом в Battle.net-чат. Чат намеренно не исправлен;
в рабочую сборку не входят широкая нижняя click-through-зона, принудительный
возврат фокуса, X11 RECORD-listener, `no_follow_mouse` и `cursor:no_warps`.

## Быстрая карта каталога

- `README.md` — полная эксплуатационная инструкция, диагностика, обновление и
  восстановление.
- `PATCH-MANIFEST.txt` — краткий состав функциональных изменений сборки.
- `SHA256SUMS` — контроль целостности всего переносимого комплекта.
- `hdt-wine-functional.patch` — единый патч для чистого upstream v1.55.3.
- `hdt-wine-functional-v1.55.3.patch` — его версионная копия.
- `local-*.patch` — отдельные локальные изменения для разбора и переноса на
  следующую версию.
- `upstream-pr-4741.patch` — исходный Wine-фикс интерактивных кнопок.
- `config/` — точные копии launcher, guard, Rofi, desktop- и Lutris-файлов.
- `assets/` — исходная иконка Hearthstone для Waybar.
- `local-recent-games.patch` — история последних 20 игр, кнопка раскрытия и
  тесты сохранения старых матчей.
- `artifacts/hdt-working-v1.55.3-recent-games.tar.zst` — текущий полный
  автономный снимок рабочего каталога HDT, включая exe, DLL, ресурсы и PDB.
- `artifacts/hdt-working-v1.55.3-recent-games.contents.sha256` — хэши всех 169
  файлов внутри текущего рабочего снимка.
- `artifacts/hdt-working-v1.55.3-pre-chat.tar.zst` — исторический снимок до
  экспериментов с чатом и до расширенной истории игр.

## Зафиксированная версия

```text
HDT:                 1.55.3.7390
Upstream tag:        v1.55.3
Upstream commit:     9e92f445f22d04f02c179c5cf6060f220dfe8929
Patched executable:  41e8df362b951d81a0c4b897f1e264a7030bfc4ad90098bfa8c5fe2e45bbcc72
Archive SHA-256:     2f576a33231581e20b217ab9aa9f55c8cbd5b91c133c7e5ad9870ea7cd549ac6
Contents manifest:   3fc91f8e2b115dd772fdbcd33e52cbca63ec49c9f387f14a4dd462228134e7fd
```

Рабочий exe содержит все проверяемые guard-маркеры: Wine-кнопки,
фиксированную геометрию, tooltip без нулевого состояния, отключённую
window-level opacity mask и центрально-левую Battlegrounds click-through-зону.
Панель `Latest Games` дополнительно раскрывает 20 последних матчей с финальными
билдами и сохраняет минимум 20 записей независимо от их возраста.

## Проверка комплекта

Из корня этого каталога:

```bash
sha256sum -c SHA256SUMS
tar --zstd -tf artifacts/hdt-working-v1.55.3-recent-games.tar.zst >/dev/null
```

Для глубокой проверки содержимого архива:

```bash
tmp="$(mktemp -d)"
tar --zstd -xf artifacts/hdt-working-v1.55.3-recent-games.tar.zst -C "$tmp"
(cd "$tmp" && sha256sum -c \
  /home/mike/projects/deck-tracker-fix/artifacts/hdt-working-v1.55.3-recent-games.contents.sha256)
rm -rf "$tmp"
```

## Автономное восстановление

Выполнять при полностью закрытом HDT. Hearthstone рекомендуется тоже закрыть,
если восстанавливается вся установка, а не только overlay между матчами.

```bash
project=/home/mike/projects/deck-tracker-fix
install='/home/mike/Games/hs/battlenet/drive_c/users/steamuser/AppData/Local/HearthstoneDeckTracker/Hearthstone Deck Tracker'
snapshot='/home/mike/.local/share/lutris/backups/hdt-overlay/working-current-wine'
tmp="$(mktemp -d)"

tar --zstd -xf "$project/artifacts/hdt-working-v1.55.3-recent-games.tar.zst" -C "$tmp"
rsync -a --delete "$tmp/" "$install/"
rsync -a --delete "$tmp/" "$snapshot/"
rm -rf "$tmp"

~/.local/share/lutris/scripts/hdt-prelaunch.py --status
```

После этого запускать единственную запись Lutris **Hearthstone + Deck Tracker**.
Для перезапуска только overlay во время уже запущенной игры использовать пункт
Rofi **«Перезапустить HS Overlay»**.

## Перенос на новую версию

1. Прочитать раздел «Обновление HDT» в `README.md` и сделать датированную
   резервную копию текущей установки.
2. Взять исходники точного нового тега HDT.
3. Перенести `hdt-wine-functional.patch` по смыслу; не копировать старый exe в
   каталог с DLL другой версии.
4. Не возвращать изменения для Battle.net-чата, перечисленные в начале файла.
5. Собрать x86-64 exe, проверить все guard-маркеры и только затем заменить весь
   официальный каталог одной версии.
6. После живой проверки обновить архив, manifest, README и `SHA256SUMS`.

Исходный рабочий каталог на этой машине:

```text
/home/mike/projects/Hearthstone-Deck-Tracker-v1.55.3
```

Переносимым источником истины являются патчи и архив в этом проекте: исходный
worktree может содержать build-артефакты и не требуется для восстановления.
