const path = require('path');
let HtmlWebpackPlugin = require('html-webpack-plugin');

class InlineSourcePlugin {
    apply(compiler) {
        compiler.hooks.compilation.tap('InlineSourcePlugin', (compilation) => {
            const hooks = HtmlWebpackPlugin.getHooks(compilation);

            hooks.alterAssetTagGroups.tapAsync('InlineSourcePlugin', (data, cb) => {
                const getAssetSource = (assetName) => {
                    const asset = compilation.getAsset
                        ? compilation.getAsset(assetName)
                        : compilation.assets[assetName];
                    if (!asset) return null;
                    if (asset.source && typeof asset.source.source === 'function') {
                        return asset.source.source();
                    }
                    if (asset.source && typeof asset.source === 'function') {
                        return asset.source();
                    }
                    return asset.source || null;
                };

                const inlineTag = (tag) => {
                    if (tag.tagName === 'script' && tag.attributes && tag.attributes.src) {
                        const assetName = tag.attributes.src.replace(/^\//, '');
                        const source = getAssetSource(assetName);
                        if (source) {
                            return {
                                tagName: 'script',
                                voidTag: false,
                                attributes: { type: 'application/javascript' },
                                innerHTML: source
                            };
                        }
                    }

                    if (tag.tagName === 'link' && tag.attributes && tag.attributes.href) {
                        const rel = tag.attributes.rel || '';
                        if (rel.toLowerCase() === 'stylesheet') {
                            const assetName = tag.attributes.href.replace(/^\//, '');
                            const source = getAssetSource(assetName);
                            if (source) {
                                return {
                                    tagName: 'style',
                                    voidTag: false,
                                    attributes: { type: 'text/css' },
                                    innerHTML: source
                                };
                            }
                        }
                    }

                    return tag;
                };

                data.headTags = data.headTags.map(inlineTag);
                data.bodyTags = data.bodyTags.map(inlineTag);
                cb(null, data);
            });
        });
    }
}
// const PreloadWebpackPlugin = require('preload-webpack-plugin');

module.exports = {
    publicPath: '',
    outputDir: path.resolve(__dirname, 'cloudsplaining', 'output', 'dist'),
    filenameHashing: false,
    pages: {
        index: {
            // entry for the page
            entry: 'cloudsplaining/output/src/main.js',
            // the source template
            template: 'cloudsplaining/output/public/index.html',
            // output as dist/index.html
            filename: 'index.html',
            chunks: ['chunk-vendors', 'index']
        },
    },
    css: {extract: false},

    chainWebpack: config => {
        // config.output
        //     .filename = '[name].bundle.js';
        if (process.env.NODE_ENV === 'development') {
            config.plugins
                .delete('preload')
                .delete('prefetch');
        }
        config
            .plugin('inline-source-plugin')
            .use(InlineSourcePlugin)
        config
            .plugin('html-index')
            .tap((args) => {
                args[0] = {
                    ...(args[0] || {}),
                    inlineSource: '.(js|css)$',
                    inject: 'body',
                    scriptLoading: 'blocking',
                    template: 'cloudsplaining/output/public/index.html',
                    title: 'Cloudsplaining report',
                };
                return args;
            });
        config.optimization
            .splitChunks({
                name: false,
                chunks: 'async',
                hidePathInfo: true,
            });
        config.module
            .rule('md')
                .test(/\.md$/)
                .use('html-loader')
                .loader("html-loader")
                .end()
                .use('markdown-loader')
                .loader("markdown-loader")
    }
}
