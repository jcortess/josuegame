import { gameState } from '../utils/gameState.js';

export default class LevelReportScene extends Phaser.Scene {
    constructor() {
        super('LevelReportScene');
    }

    create() {
        this.add.text(100, 100, `Correct: ${gameState.correct}`);
        this.add.text(100, 150, `Mistakes: ${gameState.mistakes.length}`);

        this.add.text(100, 300, "Continue")
            .setInteractive()
            .on('pointerdown', () => {
                gameState.levelIndex++;
                this.scene.start('LevelIntroScene');
            });
    }
}