const path = require('path');
let HtmlWebpackPlugin = require('html-webpack-plugin');
let HtmlWebpackInlineSourcePlugin = require('html-webpack-inline-source-plugin');

module.exports = {
    publicPath: '',
    outputDir: path.resolve(__dirname, 'cloudsplaining', 'output', 'dist'),
    filenameHashing: false,
    configureWebpack: {
        output: {
            filename: '[name].bundle.js',
            // path: path.resolve(__dirname, 'dist'),
        },
        plugins: [
            new HtmlWebpackInlineSourcePlugin(),
            new HtmlWebpackPlugin({
                inlineSource: '.(js|css)$', // embed all javascript and css inline
                inject: true,
                template: 'public/index.html',  //template file to embed the source
                title: 'Cloudsplaining report',
            }),
        ],
        optimization: {
            splitChunks: {
                name: false,
                chunks: 'async',
                hidePathInfo: true,
            }
        },
        module: {
            rules: [
                {
                  test: /\.md$/,
                  use: [
                    // {
                    //   loader: "raw-loader",
                    // },
                    {
                      loader: "html-loader"
                    },
                    {
                      loader: "markdown-loader",
                    },
                  ]
                },
            ]
        }
    },
    css: { extract: false }
}
