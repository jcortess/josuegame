import { gameState } from '../utils/gameState.js';

export default class LevelIntroScene extends Phaser.Scene {
    constructor() {
        super('LevelIntroScene');
    }

    preload() {
        this.load.json('questions', 'data/question_bank_20_per_topic.json');
    }

    create() {
        const data = this.cache.json.get('questions');

        if (!data || !data.levels || data.levels.length === 0) {
            this.add.text(100, 100, 'Question bank not found or invalid.', {
                fontSize: '28px',
                color: '#ff4444'
            });
            return;
        }

        if (gameState.levelIndex >= data.levels.length) {
            this.scene.start('ResultsScene');
            return;
        }

        const level = data.levels[gameState.levelIndex];
        const isLastLevel = gameState.levelIndex === data.levels.length - 1;

        this.cameras.main.setBackgroundColor('#1f2a44');

        this.add.text(550, 120, 'Level Intro', {
            fontSize: '42px',
            color: '#ffffff',
            fontStyle: 'bold'
        }).setOrigin(0.5);

        this.add.text(550, 220, `Level ${gameState.levelIndex + 1}: ${level.name}`, {
            fontSize: '34px',
            color: '#ffe082'
        }).setOrigin(0.5);

        this.add.text(550, 280, `Topic: ${level.topic}`, {
            fontSize: '28px',
            color: '#ffffff'
        }).setOrigin(0.5);

        this.add.text(550, 340, `Boss: ${level.boss}`, {
            fontSize: '28px',
            color: '#ffb3b3'
        }).setOrigin(0.5);

        this.add.text(550, 430, `Player: ${gameState.playerName}`, {
            fontSize: '24px',
            color: '#bde0fe'
        }).setOrigin(0.5);

        this.add.text(550, 470, `Lives: ${gameState.lives}   Score: ${gameState.score}`, {
            fontSize: '24px',
            color: '#caffbf'
        }).setOrigin(0.5);

        const button = this.add.rectangle(550, 580, 260, 70, 0x4caf50)
            .setStrokeStyle(3, 0xffffff)
            .setInteractive({ useHandCursor: true });

        this.add.text(550, 580, isLastLevel ? 'Start Final Boss' : 'Start Level', {
            fontSize: '28px',
            color: '#ffffff',
            fontStyle: 'bold'
        }).setOrigin(0.5);

        button.on('pointerdown', () => {
            if (isLastLevel) {
                this.scene.start('BossIntroScene');
            } else {
                this.scene.start('QuestionScene');
            }
        });

        this.input.keyboard.once('keydown-SPACE', () => {
            if (isLastLevel) {
                this.scene.start('BossIntroScene');
            } else {
                this.scene.start('QuestionScene');
            }
        });

        this.input.keyboard.once('keydown-ENTER', () => {
            if (isLastLevel) {
                this.scene.start('BossIntroScene');
            } else {
                this.scene.start('QuestionScene');
            }
        });
    }
}