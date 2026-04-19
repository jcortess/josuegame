import { gameState } from '../utils/gameState.js';

export default class QuestionScene extends Phaser.Scene {
    constructor() {
        super('QuestionScene');
    }

    preload() {
        this.load.json('questions', 'data/question_bank_20_per_topic.json');
    }

    create() {
        const data = this.cache.json.get('questions');

        const level = data.levels[gameState.levelIndex];

        gameState.questions = Phaser.Utils.Array.Shuffle(level.questions).slice(0, 15);

        this.currentQ = 0;

        this.hero = this.add.circle(100, 500, 20, 0x00ff00);

        this.monster = this.add.rectangle(800, 200, 100, 100, 0xff0000);
        this.monsterText = this.add.text(750, 150, "Idle");

        this.createQuestion();
    }

    createQuestion() {
        const q = gameState.questions[this.currentQ];

        this.add.text(100, 50, q.prompt);
        this.add.text(100, 100, q.question);

        this.options = [];

        q.options.forEach((opt, i) => {
            let btn = this.add.rectangle(200 + i * 200, 400, 150, 80, 0x3333ff)
                .setInteractive()
                .on('pointerdown', () => this.answer(opt));

            this.add.text(180 + i * 200, 380, opt);

            this.options.push(btn);
        });
    }

    answer(option) {
        const q = gameState.questions[this.currentQ];

        if (option === q.answer) {
            gameState.score += 10;
            gameState.correct++;
            this.monsterText.setText("HURT 😢");
        } else {
            gameState.lives--;
            this.monsterText.setText("HAPPY 😈");

            gameState.mistakes.push({
                question: q.question,
                correct: q.answer,
                selected: option
            });

            gameState.weakTopics[q.topic] = (gameState.weakTopics[q.topic] || 0) + 1;
        }

        this.time.delayedCall(1000, () => {
            this.nextQuestion();
        });
    }

    nextQuestion() {
        this.currentQ++;

        if (this.currentQ >= gameState.questions.length) {
            this.scene.start('LevelReportScene');
        } else {
            this.scene.restart();
        }
    }

    update() {
        this.input.on('pointermove', pointer => {
            this.physics.moveTo(this.hero, pointer.x, pointer.y, 200);
        });
    }
}