# Сборка HDT 1.59.8

Установлена `1.59.8.9020` из опубликованного коммита `2698623dc0e91491671a614ae176f9db68831aa7` с патчем `../hdt-wine-functional-v1.59.8.patch`. Использован [официальный full-пакет 1.59.8](https://github.com/HearthSim/HDT-Releases/releases/tag/v1.59.8); SHA-256 проверен по digest release asset. Хэши пакета, официального exe, локальной сборки, установленного exe и архива записаны в `result.json`.

Все 53 DLL официального пакета сохранены побайтно. Добавлены `System.Resources.Extensions.dll` и PDB главной сборки. В 1.59.8 upstream встраивает локализации в главный exe, поэтому отдельных DLL меньше, чем в предыдущем выпуске.

При переносе патча разрешён один конфликт в `AnimatedCard.EnsureTile`. Upstream перенёс регистрацию Battlegrounds-подсказки на `Grid`; она сохранена. Локальное направление превью теперь задаётся и для `Grid`, и для вложенной плитки. Сохранены пул карточек, новая логика обновления их состояния, рейтинг solo/duos и подписки Tier7.

`RunRegressionTests.cs` запускает существующие тесты HDT через reflection под .NET Framework/Wine. В тестовый каталог скопированы итоговый exe с Wine-исправлением прозрачности и официальные DLL. `regression-tests.log` подтверждает 15 успешных проверок истории 20 матчей, Wine-кнопок и рейтинга. `guard.log` подтверждает все маркеры совместимости. Патч проверен через `git apply --check` на чистом дереве коммита выпуска и `git diff --check` в рабочем дереве.

Трекер перезапущен в рабочем префиксе через UMU/GE-Proton11-12. Главное окно появилось, журнал подтвердил `1.59.8.9020`. Данные проверки сохранены в `startup-verification.json`. Hearthstone был закрыт, поэтому overlay в матче не проверялся.

Архив `../artifacts/hdt-working-v1.59.8-recent-games.tar.zst` содержит 157 файлов. После распаковки проверены все хэши соответствующего `.contents.sha256`. Пользовательские настройки, история, токены и плагины из рабочей установки в архив не входят. Предыдущая установка и пользовательский Roaming-каталог сохранены по пути из `result.json`.

## Повторная сборка

Для восстановления готового приложения достаточно архива и манифеста. Для сборки нужны Windows .NET SDK 8.0.100 под Wine, Linux SDK для restore, reference assemblies .NET Framework 4.7.2 и зависимости NuGet.

1. Подготовить дерево точного коммита выпуска и применить `hdt-wine-functional-v1.59.8.patch`. Скачать официальный `HearthstoneDeckTracker-1.59.8-full.nupkg` и проверить SHA-256 из `result.json`.
2. Поместить DLL из `lib/net472` официального пакета в исходный `lib/`, как в `prep.sh`. Взять HDT-Localization на коммите `7d7045c17c700ea24299732330da8a8e62fd8788`, скопировать `Strings*.resx` в `Properties/`, а `CHANGELOG.md` в `Resources/`.
3. Временно включить `GenerateResourceUsePreserializedResources`, добавить `System.Resources.Extensions` 4.7.1 и разрешить пропуск `BeforeBuildMigrated` через `SkipGenerateDesignerFiles`. Выполнить restore Linux SDK с `--runtime win7-x64`, переписать пути NuGet в assets/props на Wine-пути и сгенерировать `Strings.Designer.cs` через `StronglyTypedResx.exe`.
4. Собрать Windows SDK через `script -q -e` с параметрами `Release`, `Platform=x64`, `Version=1.59.8`, `BuildNumber=9020`, `SkipGenerateDesignerFiles=true`, `--no-restore`. Аналогично собрать `HDTTests`. Восстановить исходный csproj после сборки.
5. Кандидат создать из полного официального `lib/net472`. Заменить главный exe локальной сборкой, назвать его `Hearthstone Deck Tracker.exe`, переименовать соответствующий `.exe.config`, добавить главный PDB и `System.Resources.Extensions.dll`. Проверить побайтное совпадение всех официальных DLL.
6. Запустить guard с отдельными `HDT_DIR`, `HDT_CONFIG`, `BATTLE_NET_CONFIG`, `HDT_BACKUP_ROOT`, `HDT_WORKING_SNAPSHOT`. Подставить полученный exe в тестовый каталог, выполнить регрессионные тесты. Только после этого сохранять резервную копию и заменять рабочую установку под lock recovery launcher.

Скрипты этой машины находятся в `$HOME/.cache/hdt-build/v1.59.8/`: `prep.sh`, `build.sh`, `tests-build.sh`, `prepare-candidate.py`, `deploy.py`. Рабочий исходный каталог — `$HOME/projects/Hearthstone-Deck-Tracker-v1.59.8`. Временные изменения csproj не включены в сохранённый функциональный патч.
