myChart1 = echarts.init(document.getElementById("chart1"));
myChart2 = echarts.init(document.getElementById("chart2"));
myChart3 = echarts.init(document.getElementById("chart3"));

option1 = {
    series: [
        {
            name: '节点状态',
            type: 'gauge',
            splitNumber: 5,  // 刻度切几个
            radius: '90%',   // 图形大小
            title:{
                show:true,
                offsetCenter: [0, '90%'],
                color:'#2F4056',
                fontSize:13,
                fontWeight: 'bold',
                backgroundColor: '#FFF',
                borderRadius:18,
                padding: 6,
                shadowColor:"#C3Cfff",
                shadowBlur:6,
            },
            axisLine: {        
                lineStyle: {       
                    color: [[0.2, '#D94600'],[0.8,'#000079'],[1,'#009393']],
                    width: 10,
                    shadowColor: '#000', //默认透明
                    shadowBlur: 0,
                }
            },
            detail: {
                formatter: '{value}%',
                fontSize: 16,
            },
            data: [{value: 50, name: '节点状态'}]
        }
    ]
};

option2 = {
    series: [
        {
            name: 'CPU',
            type: 'gauge',
            splitNumber: 5,  // 刻度切几个
            radius: '90%',   // 图形大小
            title:{
                show:true,
                offsetCenter: [0, '90%'],
                color:'#2F4056',
                fontSize:13,
                fontWeight: 'bold',
                backgroundColor: '#FFF',
                borderRadius:18,
                padding: 6,
                shadowColor:"#C3Cfff",
                shadowBlur:6,
            },
            axisLine: {            // 坐标轴线
                lineStyle: {       // 属性lineStyle控制线条样式
                    color: [[0.2, '#009393'], [0.8, '#000079'], [1, '#D94600']],
                    width: 10,
                    shadowColor: '#000', //默认透明
                    shadowBlur: 0,
                }
            },
            detail: {
                formatter: '{value}%',
                fontSize: 16,
            },
            data: [{value: 50, name: 'CPU使用量'}]
        }
    ]
};
option3 = {
    series: [
        {
            name: '内存',
            type: 'gauge',
            splitNumber: 5,  // 刻度切几个
            radius: '90%',   // 图形大小
            title:{
                show:true,
                offsetCenter: [0, '90%'],
                color:'#2F4056',
                fontSize:13,
                fontWeight: 'bold',
                backgroundColor: '#FFF',
                borderRadius:18,
                padding: 6,
                shadowColor:"#C3Cfff",
                shadowBlur:6,
            },
            axisLine: {            // 坐标轴线
                lineStyle: {       // 属性lineStyle控制线条样式
                    color: [[0.2, '#009393'], [0.8, '#000079'], [1, '#D94600']],
                    width: 10,
                    shadowColor: '#000', //默认透明
                    shadowBlur: 0,
                }
            },
            detail: {
                formatter: '{value}%',
                fontSize: 16,
            },
            data: [{value: 50, name: '内存使用量'}],
        }
    ]
};

myChart1.setOption(option1, true);
myChart2.setOption(option2, true);
myChart3.setOption(option3, true);
