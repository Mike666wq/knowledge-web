// VitePress 主题入口
import DefaultTheme from 'vitepress/theme'
import NotesTree from './components/NotesTree.vue'
import RotatingCards from './components/RotatingCards.vue'
import GlassCards from './components/GlassCards.vue'
import TerminalButton from './components/TerminalButton.vue'
import ColorPalette from './components/ColorPalette.vue'
import FolderNode from './components/FolderNode.vue'
import AnimatedFace from './components/AnimatedFace.vue'
import MacCode from './components/MacCode.vue'
import ThemeModeCard from './components/ThemeModeCard.vue'
import FlipBook from './components/FlipBook.vue'
import PlaneLoader from './components/PlaneLoader.vue'
import ClientLoader from './components/ClientLoader.vue'
import DoodleMenu from './components/DoodleMenu.vue'
import MemberCard from './components/MemberCard.vue'
import PhoneMock from './components/PhoneMock.vue'
import WeatherCard from './components/WeatherCard.vue'
import AuthorCard from './components/AuthorCard.vue'
import Stacked3DCard from './components/Stacked3DCard.vue'
import UfoBg from './components/UfoBg.vue'
import EmojiMarquee from './components/EmojiMarquee.vue'
import KeyViz from './components/KeyViz.vue'
import CubeLoader from './components/CubeLoader.vue'
import Ghost from './components/Ghost.vue'
import Panda from './components/Panda.vue'
import Panda2 from './components/Panda2.vue'
import BrowserMockup from './components/BrowserMockup.vue'
import FigmaFlow from './components/FigmaFlow.vue'
import Terminal from './components/Terminal.vue'
import MusicPlayer from './components/MusicPlayer.vue'
import RetroTV from './components/RetroTV.vue'
import IosSettings from './components/IosSettings.vue'
import SunPlanet from './components/SunPlanet.vue'
import EarthPlanet from './components/EarthPlanet.vue'
import CardFan from './components/CardFan.vue'
import WaterDrop from './components/WaterDrop.vue'
import PriceCardA from './components/PriceCardA.vue'
import ViperCard from './components/ViperCard.vue'
import PriceCardB from './components/PriceCardB.vue'
import RedCardDeck from './components/RedCardDeck.vue'
import CubeGrid from './components/CubeGrid.vue'
import Layout from './ShellLayout.vue'  // ★ 自定义 Layout（注入主题切换按钮）
import './custom.css'  // ★ 引入自定义主题 CSS

export default {
  extends: DefaultTheme,
  Layout,  // ★ 覆盖默认 Layout

  // ★ 全局注册自定义组件
  enhanceApp({ app }) {
    if (DefaultTheme.enhanceApp) {
      DefaultTheme.enhanceApp({ app })
    }
    app.component('NotesTree', NotesTree)
    app.component('RotatingCards', RotatingCards)
    app.component('GlassCards', GlassCards)
    app.component('TerminalButton', TerminalButton)
    app.component('ColorPalette', ColorPalette)
    app.component('FolderNode', FolderNode)
    app.component('AnimatedFace', AnimatedFace)
    app.component('MacCode', MacCode)
    app.component('ThemeModeCard', ThemeModeCard)
    app.component('FlipBook', FlipBook)
    app.component('PlaneLoader', PlaneLoader)
    app.component('ClientLoader', ClientLoader)
    app.component('DoodleMenu', DoodleMenu)
    app.component('MemberCard', MemberCard)
    app.component('PhoneMock', PhoneMock)
    app.component('WeatherCard', WeatherCard)
    app.component('AuthorCard', AuthorCard)
    app.component('Stacked3DCard', Stacked3DCard)
    app.component('UfoBg', UfoBg)
    app.component('EmojiMarquee', EmojiMarquee)
    app.component('KeyboardView', KeyViz)
    app.component('CubeLoader', CubeLoader)
    app.component('Ghost', Ghost)
    app.component('Panda', Panda)
    app.component('Panda2', Panda2)
    app.component('BrowserMockup', BrowserMockup)
    app.component('FigmaFlow', FigmaFlow)
    app.component('Terminal', Terminal)
    app.component('MusicPlayer', MusicPlayer)
    app.component('RetroTV', RetroTV)
    app.component('IosSettings', IosSettings)
    app.component('SunPlanet', SunPlanet)
    app.component('EarthPlanet', EarthPlanet)
    app.component('CardFan', CardFan)
    app.component('WaterDrop', WaterDrop)
    app.component('PriceCardA', PriceCardA)
    app.component('ViperCard', ViperCard)
    app.component('PriceCardB', PriceCardB)
    app.component('RedCardDeck', RedCardDeck)
    app.component('CubeGrid', CubeGrid)
  }
}