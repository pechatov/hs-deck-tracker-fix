# Wine-фиксы для официальной HDT 1.59.3

Установлена `1.59.3.9015` из [официального full-пакета](https://github.com/HearthSim/HDT-Releases/releases/tag/v1.59.3), опубликованного 14 октября 2026 года. Локальные изменения перенесены в IL и три BAML-ресурса. Все 69 официальных DLL совпадают побайтно; добавлена `System.Resources.Extensions.dll`.

На 18 октября исходники выпуска не опубликованы. Последний публичный коммит `555499e632ee5027032c94068a86819b6c94b087` относится к 1.59.2. Он используется для чистой сборки и донора исправленных методов. Exe этих сборок не устанавливаются. Версионный патч донора — `../hdt-wine-functional-v1.59.3-donor.patch`.

`Weave.cs` проверяет совпадение заменяемых методов официального exe с чистой публичной сборкой, включая `MoveNext` async-методов. Допускаются различия в путях диагностических сообщений и номерах автоматически сгенерированных классов. `MergeBamlResources.cs` дополнительно требует побайтного совпадения трёх исходных BAML-ресурсов с чистой сборкой. Несовпадение останавливает перенос.

В официальном конструкторе `BattlegroundsSessionViewModel` добавлены только инициализаторы двух списков. Его существующий код и подписки сохранены. Аудит подтверждает 18 заменённых методов, 62 добавленных метода и два метода, которые используют изменённую guard-скриптом строку прозрачности. Остальные 26 288 исходных методов и 408 BAML-ресурсов совпадают с официальным выпуском.

`regression-tests.log` подтверждает 15 успешных тестов истории игр, Wine-кнопок и рейтинга solo/duos. `jit-verification.log` содержит проверку подготовки 80 изменённых методов и вспомогательных методов. Эти проверки выполнялись против того же exe, который установлен. `guard.log` подтверждает все маркеры совместимости и рабочий snapshot. `result.json`, `binary-verification.json` и `weave-audit.json` содержат хэши и состав изменений.

Трекер запущен через UMU/GE-Proton11-9 в рабочем префиксе. Появилось главное окно, журнал подтвердил `1.59.3.9015` и .NET Framework `528049`. Hearthstone был закрыт, поэтому работа overlay в матче не проверялась. В журнале есть обработанная самим HDT ошибка `Update.exe not found`: официальный Squirrel-вариант запущен из переносимого каталога. Инициализация после неё продолжается; автообновления закреплены guard-скриптом.

## Повторный перенос

Готовый архив `../artifacts/hdt-working-v1.59.3-recent-games.tar.zst` содержит 172 файла и не требует сборки. Для повторного переноса нужны Linux и Windows .NET SDK 8, Wine с .NET Framework или Mono, reference assemblies .NET Framework 4.7.2 и Mono.Cecil 0.11.6. Окружение этой машины находится в `$HOME/.cache/hdt-build`.

1. Скачать `HearthstoneDeckTracker-1.59.3-full.nupkg` и проверить SHA-256 `9278d4f043d693c02d773c2b01ff7fecdaeea9723cdf7a9388f06ed8f7ed8a0b`. Оригинальный exe имеет SHA-256 `f1e515eb9770870d22664c3be1c08ba218fd3db508d13a31f1edf16dadf85943`.
2. Подготовить два дерева публичного коммита `555499e6`. В одно применить патч донора. Оба собрать с DLL официального 1.59.3, Localization `e1411841bec3ccad4cfb575e970fa136fdd10b7c`, параметрами `Release`, `Platform=x64`, `Version=1.59.3`, `BuildNumber=9015` и одинаковыми временными правками генерации resx и `System.Resources.Extensions`. Под Wine 11.19 Windows SDK запускается через `script -q -e`, чтобы не падать в `ConsolePal.SetConsoleOutputEncoding` при перенаправлении вывода.
3. Собрать `weaver.csproj`. Передать через `HDT_CECIL_REFERENCE_DIRS` разделённые двоеточием каталоги reference assemblies, их `Facades` и официального `lib/net472`. Эта переменная нужна для `weave` и `attach`.
4. Выполнить `weaver.dll weave <официальный-exe> <exe-донора> <чистый-exe> <woven-exe>`. Командой `weaver.dll resources <exe> <output.resources>` выгрузить `HearthstoneDeckTracker.g.resources` из официального exe, донора и чистой сборки.
5. Скомпилировать `MergeBamlResources.cs` под .NET Framework. Вызвать его с четырьмя Windows-путями: официальный `.resources`, `.resources` донора, выходной `.resources`, `.resources` чистой сборки. Вставить результат командой `weaver.dll attach <woven-exe> <выходной.resources> <patched-exe>`.
6. Скопировать полный официальный `lib/net472` в каталог-кандидат. Заменить главный exe исправленным, переименовать его в `Hearthstone Deck Tracker.exe`, а `.exe.config` — соответственно. Добавить `System.Resources.Extensions.dll` из сборки. Главного PDB в этом официальном пакете нет.
7. Запустить изолированный guard с отдельными `HDT_DIR`, `HDT_CONFIG`, `BATTLE_NET_CONFIG`, `HDT_BACKUP_ROOT` и `HDT_WORKING_SNAPSHOT`. Проверить IL через `verify-binary.py`, загрузку методов через `PrepareWineMethods.cs` и тесты через `RunRegressionTests.cs`. В тестовый каталог копируется итоговый exe под именем `HearthstoneDeckTracker.exe` и официальные DLL; тестовая сборка запускается по её исходному пути, чтобы проверки XAML нашли корень проекта.
8. Сохранить установку, snapshot и пользовательский Roaming-каталог. Под lock `hdt-overlay-restart.lock` закрыть только HDT, заменить каталог с сохранением `Plugins/`, запустить guard и проверить запуск. Для восстановления использовать архив и манифест, описанные в основном README.

Локальные скрипты подготовки находятся в `$HOME/.cache/hdt-build/v1.59.3/{donor,baseline}/`, проверки и установки — в `prepare-candidate.py`, `verify-binary.py`, `deploy.py` и `check-startup.py` этого же каталога. Архив состоит из файлов кандидата; пользовательские данные и токены в него не включены.
