import { gameState } from '../utils/gameState.js';

export default class BossIntroScene extends Phaser.Scene {
    constructor() {
        super('BossIntroScene');
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

        this.cameras.main.setBackgroundColor('#3b0a45');

        this.add.text(550, 110, 'FINAL BOSS', {
            fontSize: '48px',
            color: '#ff4d6d',
            fontStyle: 'bold'
        }).setOrigin(0.5);

        this.add.text(550, 210, level.boss, {
            fontSize: '38px',
            color: '#ffd166',
            fontStyle: 'bold'
        }).setOrigin(0.5);

        this.add.text(550, 290, 'Mixed questions are coming!', {
            fontSize: '28px',
            color: '#ffffff'
        }).setOrigin(0.5);

        this.add.text(550, 340, 'Be careful: this is the last battle.', {
            fontSize: '26px',
            color: '#ffdddd'
        }).setOrigin(0.5);

        this.add.text(550, 410, `Player: ${gameState.playerName}`, {
            fontSize: '24px',
            color: '#bde0fe'
        }).setOrigin(0.5);

        this.add.text(550, 450, `Lives: ${gameState.lives}   Score: ${gameState.score}`, {
            fontSize: '24px',
            color: '#caffbf'
        }).setOrigin(0.5);

        const button = this.add.rectangle(550, 570, 300, 80, 0xd90429)
            .setStrokeStyle(3, 0xffffff)
            .setInteractive({ useHandCursor: true });

        this.add.text(550, 570, 'Fight the Boss', {
            fontSize: '30px',
            color: '#ffffff',
            fontStyle: 'bold'
        }).setOrigin(0.5);

        button.on('pointerdown', () => {
            this.scene.start('QuestionScene', { bossMode: true });
        });

        this.input.keyboard.once('keydown-SPACE', () => {
            this.scene.start('QuestionScene', { bossMode: true });
        });

        this.input.keyboard.once('keydown-ENTER', () => {
            this.scene.start('QuestionScene', { bossMode: true });
        });
    }
}