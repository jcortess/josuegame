import MenuScene from './scenes/MenuScene.js';
import LevelIntroScene from './scenes/LevelIntroScene.js';
import QuestionScene from './scenes/QuestionScene.js';
import LevelReportScene from './scenes/LevelReportScene.js';
import BossIntroScene from './scenes/BossIntroScene.js';
import ResultsScene from './scenes/ResultsScene.js';

const config = {
    type: Phaser.AUTO,
    width: 1100,
    height: 720,
    backgroundColor: '#1e1e2f',
    scene: [
        MenuScene,
        LevelIntroScene,
        QuestionScene,
        LevelReportScene,
        BossIntroScene,
        ResultsScene
    ]
};

new Phaser.Game(config);