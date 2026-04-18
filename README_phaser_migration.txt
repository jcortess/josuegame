Phaser HTML5 migration

Files:
- josue_english_adventure_phaser.html
- question_bank_20_per_topic.json

How it works:
- The HTML file includes a built-in default question bank.
- If you place question_bank_20_per_topic.json beside it and serve the folder over HTTP,
  the game will try to load that external file first.
- If fetch fails, it falls back to the built-in bank.

Run locally:
- simplest: use a small local server, for example:
  python -m http.server 8000
- then open:
  http://localhost:8000/josue_english_adventure_phaser.html

Controls:
- Menu: click buttons
- Level intro / boss intro / level report: click or SPACE
- Question scene: click answer doors or press 1 / 2 / 3
- Results: S downloads report, R returns to menu

Notes:
- Progress uses browser localStorage
- Report export is text download in the browser
- This is a Phaser/HTML5 migration of the uploaded Pygame build structure
