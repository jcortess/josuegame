import { gameState } from '../utils/gameState.js';

export default class QuestionScene extends Phaser.Scene {
    constructor() {
        super('QuestionScene');
    }

    preload() {
        this.load.json('questions', 'data/question_bank_20_per_topic.json');
        this.load.image('hero', 'assets/hero.png');
        this.load.image('monster', 'assets/monster.png');
    }

    create() {
        const data = this.cache.json.get('questions');
        const level = data.levels[gameState.levelIndex];

        //Cantidad de preguntas para pasar de nivel
        gameState.questions = Phaser.Utils.Array.Shuffle(level.questions).slice(0, gameState.questionsPerLevel); //gameState.js
        gameState.total = gameState.questions.length;
        this.currentQ = 0;

        //Creación de heroe
        this.hero = this.add.image(100, 500, 'hero');
        this.hero.setDisplaySize(90, 90);
        this.hero.setDepth(100);
        this.hero.setAlpha(0.95); //transparencia
        this.hero.setBlendMode(Phaser.BlendModes.ADD);

        this.targetHeroX = this.hero.x;
        this.targetHeroY = this.hero.y;

        this.input.on('pointermove', (pointer) => {
            this.targetHeroX = Phaser.Math.Clamp(pointer.x, 45, this.scale.width - 45);
            this.targetHeroY = Phaser.Math.Clamp(pointer.y, 45, this.scale.height - 45);
        });

        this.monster = this.add.image(840, 260, 'monster');
        this.monster.setDisplaySize(260, 260);
        this.monster.setDepth(50);

        this.monsterText = this.add.text(760, 110, 'Idle', {
            fontSize: '24px',
            color: '#ffffff',
            fontStyle: 'bold',
            backgroundColor: '#000000'
        });
        this.monsterText.setDepth(51);

        this.questionText = null;
        this.promptText = null;
        this.optionTexts = [];
        this.options = [];
        this.isAnswering = false;

        this.createQuestion();
    }

    createQuestion() {
        if (this.promptText) this.promptText.destroy();
        if (this.questionText) this.questionText.destroy();

        if (this.options && this.options.length) {
            this.options.forEach(btn => btn.destroy());
        }

        if (this.optionTexts && this.optionTexts.length) {
            this.optionTexts.forEach(txt => txt.destroy());
        }

        this.options = [];
        this.optionTexts = [];

        const q = gameState.questions[this.currentQ];

        this.promptText = this.add.text(100, 50, q.prompt).setDepth(10);
        this.questionText = this.add.text(100, 100, q.question).setDepth(10);

        this.options = [];

        q.options.forEach((opt, i) => {
            const btn = this.add.rectangle(200 + i * 200, 400, 150, 80, 0x3333ff)
                .setDepth(20)
                .setInteractive({ useHandCursor: true })
                .on('pointerdown', () => this.answer(opt));

            const txt = this.add.text(180 + i * 200, 380, opt).setDepth(21);

            this.options.push(btn);
            this.optionTexts.push(txt);
        });
    }

    answer(option) {
        if (this.isAnswering) return;
            this.isAnswering = true;

        const q = gameState.questions[this.currentQ];

        if (option === q.answer) {
            gameState.score += 10;
            gameState.correct++;
            this.monsterText.setText('HURT 😢');
        } else {
            gameState.lives--;
            this.monsterText.setText('HAPPY 😈');

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
        this.isAnswering = false;

        if (this.currentQ >= gameState.questions.length) {
            if (gameState.correct >= gameState.minCorrectToPass) {
                this.scene.start('LevelReportScene');
            } else {
                gameState.correct = 0;
                gameState.mistakes = [];
                this.scene.start('LevelIntroScene'); // repetir nivel
            }
        } else {
            this.createQuestion();
        }
    }

    update() {
        if (!this.hero) return;

        this.hero.x = Phaser.Math.Linear(this.hero.x, this.targetHeroX, 0.12);
        this.hero.y = Phaser.Math.Linear(this.hero.y, this.targetHeroY, 0.12);
    }
}