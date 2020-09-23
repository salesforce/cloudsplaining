const path = require('path');
let HtmlWebpackPlugin = require('html-webpack-plugin');
let HtmlWebpackInlineSourcePlugin = require('html-webpack-inline-source-plugin');
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
            .plugin('html-webpack-inline-source-plugin')
            .use(HtmlWebpackInlineSourcePlugin)
        config
            .plugin('html-webpack-plugin')
                .use(new HtmlWebpackPlugin({
                    inlineSource: '.(js|css)$', // embed all javascript and css inline
                    inject: true,
                    template: 'cloudsplaining/output/public/index.html',  //template file to embed the source
                    title: 'Cloudsplaining report',
                }
            ));
        // config
        //     .plugin('preload-webpack-plugin')
        //         .use(new PreloadWebpackPlugin({
        //             rel: 'prefetch',
        //             as: 'script'
        //         }
        //     ));
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
