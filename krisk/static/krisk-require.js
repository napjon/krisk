
//Configure require.js
if (window.require){
    window.require.config({
            baseUrl: 'nbextensions/krisk',
            paths: {
                echarts: 'echarts.min'
            }
        })
}

// Exports require module extension
module.exports = {
    load_ipython_extension: function() {}
}