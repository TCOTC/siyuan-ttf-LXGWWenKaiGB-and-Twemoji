> Recent update: support for the font configuration changes in SiYuan v3.8.2 and v3.8.3; Twemoji switched to a COLRv0 font file for WebKit compatibility

# LXGW WenKai and Twemoji

Font files sourced from: [lxgw/LxgwWenkaiGB-Lite](https://github.com/lxgw/LxgwWenkaiGB-Lite) and [lxgw/LxgwWenKai-Screen](https://github.com/lxgw/LxgwWenKai-Screen) (GB Screen edition). The latter was converted from .ttf to .woff format using [CloudConvert](https://cloudconvert.com/ttf-to-woff).

Twemoji font file sourced from: [TCOTC/twemoji-colr](https://github.com/TCOTC/twemoji-colr/)

### Notes

- This plugin may be incompatible with other font or Emoji plugins in the marketplace. Please disable other font or Emoji plugins when using this one.
- LXGW WenKai takes priority over the global default font and editor fonts selected in Settings - Appearance.
- With the "UI only" scope, only the UI text is affected, and the editor and documents keep their original fonts.
- With the "Editor only" scope, only the editor is affected and the UI keeps its original fonts.
- The font weight is pinned to 500, ignoring the weights of the fonts selected in Settings; bold text and headings keep their own weights.
- This plugin only includes GB-edition font files, which primarily use mainland standard glyphs.
