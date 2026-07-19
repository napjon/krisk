(() => {{
    const target = document.getElementById("{chartId}");
    if (!target || typeof echarts === "undefined") return;
    const myChart = echarts.getInstanceByDom(target) || echarts.init(target, "{theme}");
    const option = {option};
    myChart.setOption(option, true);
}})();
