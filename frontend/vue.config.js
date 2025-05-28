module.exports = {
  publicPath: '/',
  assetsDir: 'assets',
  indexPath: 'index.html',
  filenameHashing: true, // Оставьте хэши в именах файлов

  devServer: {
    proxy: {
      '^/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        pathRewrite: { '^/api': '' }
      }
    }
  }
}