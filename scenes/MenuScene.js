import { load, save } from '../utils/storage.js';
import { gameState } from '../utils/gameState.js';

export default class MenuScene extends Phaser.Scene {
    constructor() {
        super('MenuScene');
    }

    create() {
        this.add.text(400, 100, "English Adventure", { fontSize: '40px' });

        let input = this.add.dom(400, 200, 'input', 'width:200px');
        input.node.value = load("player_name", "Player");

        this.add.text(400, 250, "Start Game")
            .setInteractive()
            .on('pointerdown', () => {
                gameState.playerName = input.node.value;
                save("player_name", gameState.playerName);
                this.scene.start('LevelIntroScene');
            });

        this.add.text(400, 300, "Toggle Timer")
            .setInteractive()
            .on('pointerdown', () => {
                gameState.timerEnabled = !gameState.timerEnabled;
            });
    }
}