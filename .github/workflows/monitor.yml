name: Dr Althea Stock Monitor

on:
  schedule:
    - cron: "*/5 * * * *"
  workflow_dispatch:

concurrency:
  group: stock-monitor
  cancel-in-progress: false

jobs:
  check-stock:
    runs-on: ubuntu-latest
    timeout-minutes: 3

    steps:
      - name: Get repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Restore previous stock status
        uses: actions/cache/restore@v4
        with:
          path: .cache
          key: stock-state-${{ github.run_id }}
          restore-keys: |
            stock-state-

      - name: Check product availability
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python monitor.py

      - name: Save stock status
        uses: actions/cache/save@v4
        with:
          path: .cache
          key: stock-state-${{ github.run_id }}
