/**
 * Created by jiaju_cao on 2017/6/7.
 */

var isFinishLoad = false;
var currentPageIndex = 0;
var currentPageSize = 10;

var templateTemp = '<div class="template_flower">' +
    '<div class="factory_class_left" style="visibility: { fact_display1 }">' +
    '<img src="{fact_logo1}" class="fact_log">' +
    '<div style="width: 100%">' +
    '<div class="name_info">{fact_name1}</div>  ' +
    '</div>' +
    '<div style="width:100%;margin-top: 10px" class="expert_info">' +
    '{expert_org_info1}' +
    '</div>' +
    '</div>' +
    '<div class="factory_class_right" style="visibility: {fact_display2}">' +
    '<img src="{fact_logo2}" class="fact_log">' +
    '<div style="width: 100%">' +
    '<div class="name_info">{fact_name2}</div>' +
    '</div>' +
    '<div style="width:100%;margin-top: 10px"  class="expert_info">' +
    '{expert_org_info2}' +
    '</div>    </div>   ' +
    '</div>' +
    '';
window.onload=function()
{
};

$(document).ready(function()
{
    // 查询参与投票的品牌
    $.query_expert_data();

    $(window).scroll(function(){
        var srollPos = $(window).scrollTop();
        var documentHd = $(document).height();
        var winHd = $(window).height() ;

        if (srollPos + winHd > documentHd*0.9 && !isFinishLoad)
        {
             // 加载数据
            currentPageIndex = currentPageIndex + 1;
            $.query_expert_data();
        }

        });
});

$(window).resize(function(){
});

// 自定义函数
$.extend({
    get_current_query:function () {
        var rtnCmd = "/api/vote/?Command=Query_Expert&pageindex={0}&pagesize={1}";

        rtnCmd = $.StringFormat(rtnCmd, currentPageIndex.toString(),currentPageSize.toString());

        return rtnCmd;
    },
    query_expert_data: function ()
    {
        var cmdString = $.get_current_query();

        // 提取用户名
        $.get( cmdString,
            function (data)
            {
                //alert(templateTemp);
                // 检查查询状态
                var  ErrorId = data.ErrorId;
                var  Result = data.Result;
                var Datas = Result.Datas
                if (ErrorId == 200)
                {
                    if (Datas.length <= 0)
                    {
                        isFinishLoad = true;
                    }
                    for (i=0;i<Datas.length ;i=i+2 )
                    {
                        var oneCode1 = Datas[i];

                        // var isFull = false;
                        var oneCode2 = null;
                        if (i + 1 < Datas.length)
                        {
                            // isFull = true;
                            oneCode2 = Datas[i+1];
                        }
                        var oneT = $("#expertList").html();
                        if("undefined" == typeof oneT)
                        {
                            oneT = "";
                        }

                        var abcTemp = {
                            fact_display1:"visible",
                            fact_logo1:"/static/expert/" + oneCode1.faceimage + ".jpg",
                            fact_name1:oneCode1.name,
                            fact_code1:oneCode1.code,
                            expert_org_info1:oneCode1.info,
                        }

                        if (oneCode2 != null)
                        {
                            abcTemp["fact_display2"] = "visible";
                            abcTemp["fact_logo2"] = "/static/expert/" + oneCode2.faceimage + ".jpg";
                            abcTemp["fact_name2"] = oneCode2.name;
                            abcTemp["fact_code2"] = oneCode2.code;
                            abcTemp["expert_org_info2"] = oneCode2.info;

                        }
                        else
                        {
                            abcTemp["fact_display2"] = "hidden";
                        }

                        $("#expertList").html(oneT + $.format(templateTemp,abcTemp) );

                    }
                }

            },
            "json");//这里返回的类型有：json,html,xml,text
    },
    StringFormat:function() {
             if (arguments.length == 0)
                 return null;
             var str = arguments[0];
             for (var i = 1; i < arguments.length; i++) {
                 var re = new RegExp('\\{' + (i - 1) + '\\}', 'gm');
                 str = str.replace(re, arguments[i]);
             }
             return str;
        } ,
    format : function(source,args){
					var result = source;
					if(typeof(args) == "object"){
						if(args.length==undefined){
							for (var key in args) {
								if(args[key]!=undefined){
									var reg = new RegExp("({" + key + "})", "g");
									result = result.replace(reg, args[key]);
								}
							}
						}else{
							for (var i = 0; i < args.length; i++) {
								if (args[i] != undefined) {
									var reg = new RegExp("({[" + i + "]})", "g");
									result = result.replace(reg, args[i]);
								}
							}
						}
					}
					return result;
				},
});