import { gameState } from '../utils/gameState.js';
import { save, load } from '../utils/storage.js';

export default class ResultsScene extends Phaser.Scene {
    constructor() {
        super('ResultsScene');
    }

    create() {
        let high = load("high_score", 0);

        if (gameState.score > high) {
            save("high_score", gameState.score);
        }

        this.add.text(100, 100, `Score: ${gameState.score}`);
        this.add.text(100, 150, `Accuracy: ${(gameState.correct / gameState.total) * 100}%`);

        this.add.text(100, 250, "Download Report")
            .setInteractive()
            .on('pointerdown', () => {
                const text = JSON.stringify(gameState.mistakes, null, 2);

                const blob = new Blob([text], { type: "text/plain" });
                const a = document.createElement("a");
                a.href = URL.createObjectURL(blob);
                a.download = "report.txt";
                a.click();
            });
    }
}