// module.exports = class PluginLXGWTwemoji extends require('siyuan').Plugin {};

module.exports = class PluginLXGWTwemoji extends require('siyuan').Plugin {
    onload() {
        console.log("siyuan-ttf-LXGWWenKaiGB-and-Twemoji: loaded");

        // 创建 style 元素
        const styleElement = document.createElement('style');
        styleElement.id = 'snippetCSS-LXGWTwemoji';

        // 插入到 head 中
        document.head.appendChild(styleElement);

        // 获取 CSS 文件内容
        fetch('../plugins/siyuan-ttf-LXGWWenKaiGB-and-Twemoji/style.css')
            .then(response => {
                if (!response.ok) {
                    throw new Error('siyuan-ttf-LXGWWenKaiGB-and-Twemoji: Failed to load CSS file');
                }
                return response.text();
            })
            .then(cssText => {
                // 将 CSS 文本插入到 style 元素中
                styleElement.textContent = cssText;
            })
            .catch(error => {
                console.error('siyuan-ttf-LXGWWenKaiGB-and-Twemoji: Error loading CSS:', error);
            });
    }

    onunload() {
        // 移除 style 元素
        const styleElement = document.getElementById('snippetCSS-LXGWTwemoji');
        if (styleElement) {
            styleElement.remove();
        }
        
        console.log("siyuan-ttf-LXGWWenKaiGB-and-Twemoji: unloaded");
    }

    uninstall() {
        // 在卸载时也移除 style 元素
        const styleElement = document.getElementById('snippetCSS-LXGWTwemoji');
        if (styleElement) {
            styleElement.remove();
        }
        
        console.log("siyuan-ttf-LXGWWenKaiGB-and-Twemoji: uninstall");
    }
}
