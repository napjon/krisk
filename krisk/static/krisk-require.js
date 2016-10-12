define(function(){

	return {
		load_ipython_extension: function(){
			console.debug('krisk loaded')

			require.config({
				map: {
			            "*" : {
			                "echarts": "nbextensions/krisk/echarts.min",
			                "dark": "nbextensions/krisk/dark",
			                "infographic": "nbextensions/krisk/infographic",
			                "roma": "nbextensions/krisk/roma",
			                "vintage": "nbextensions/krisk/vintage",
			                "macarons": "nbextensions/krisk/macarons",
			                "shine": "nbextensions/krisk/shine",

			            }
			        }
			 // Solution above is not clean and preferable below.
			 // Forced to use it because of Jupyter issue. See
			 // https://github.com/jupyter/notebook/issues/626#issuecomment-160593027
			 	 
             // baseUrl : "nbextensions/krisk",
             // paths: {
             //      echarts: "echarts.min"

             //  }
              });
		}
	}
	
})