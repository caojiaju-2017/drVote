/**
 * Created by jiaju_cao on 2017/6/7.
 */

var userCookie=null;
var lastDate=null;
var isEnable = 1;

var isFinishLoad = false;
var currentPageIndex = 0;
var currentPageSize = 10;
var fliterString = "";
var queryLock = false;
var templateTemp = '<div class="template_flower">' +
    '<div class="factory_class_left" style="visibility: { fact_display1 }">' +
    '<img src="{fact_logo1}" class="fact_log">' +
    '<div style="width: 100%">' +
    '<div class="name_info">{fact_name1}</div>  <div class="count_info" id="{fact_code1}">得票数：{fact_vote_count1}</div>' +
    '</div>' +
    '<div style="width:100%;margin-top: 10px" id="{fact_code1}">' +
    '<img src="{vote_icon}" style="width:60%;height: 2cm" onclick="$.vote_mydata(\'{fact_code1}\')">' +
    '</div>' +
    '</div>' +
    '<div class="factory_class_right" style="visibility: {fact_display2}">' +
    '<img src="{fact_logo2}" class="fact_log">' +
    '<div style="width: 100%">' +
    '<div class="name_info">{fact_name2}</div>  <div class="count_info" id="{fact_code2}">得票数：{fact_vote_count2}</div>' +
    '</div>' +
    '<div style="width:100%;margin-top: 10px"  id="{fact_code2}">' +
    '<img src="{vote_icon}" style="width:60%;height: 2cm" onclick="$.vote_mydata(\'{fact_code2}\')">' +
    '</div>    </div>   ' +
    '</div>' +
    '';
window.onload=function()
{
    $.validCookie();
    //
    // if(navigator.userAgent.match(/MicroMessenger/i))
    // {
    //     $('body').prepend('<div style=" overflow:hidden; width:0px; height:0; margin:0 auto; position:absolute; top:-800px;"><img src="'+ "/static/Images/weblog.png" +'"></div>')
    // };
};

$(document).ready(function()
{
    // 初始化cookie数据
    $.validCookie();

    // 验证用户是否可以投票
    $.apply_permition(userCookie);

    // 查询参与投票的品牌
    $.query_vote_data();

    $(window).scroll(function(){
        var srollPos = $(window).scrollTop();
        var documentHd = $(document).height();
        var winHd = $(window).height() ;


        totalheight = parseFloat($(window).height()) + parseFloat(srollPos);
            // if(($(document).height()-range) <= totalheight  && num != maxnum) {
            //     main.append("<div style='border:1px solid tomato;margin-top:20px;color:#ac"+(num%20)+(num%20)+";height:"+elemt+"' >hello world"+srollPos+"---"+num+"</div>");
            // }
        if (srollPos + winHd > documentHd*0.9 && !isFinishLoad && !queryLock)
        {
            queryLock = true;
             // 加载数据
            currentPageIndex = currentPageIndex + 1;
            $.query_vote_data();
        }

        });

    $("#searchButton").click(function()
    {
         currentPageIndex = 0;
         fliterString = $("#searchContext").val();
         if (fliterString == "请输入搜索内容" || fliterString == "" || fliterString == "undefined" || fliterString == null)
         {
             fliterString = "";
         }

     //   重置html内容
        $("#pinPaiList").html("");
        $.query_vote_data();
     });

});

$(window).resize(function(){
    $.validCookie();
});

// 自定义函数
$.extend({
    apply_permition: function (uCookie)
    {

        // 提取用户名
        $.get("/api/vote/?Command=Query_UserInfo&cookie=" + uCookie,
            function (data)
            {
                // 检查查询状态
                var  ErrorId = data.ErrorId;
                var  Result = data.Result;

                if (ErrorId == 200)
                {
                    isEnable = parseInt(Result);
                    //alert(isEnable);
                }

            },
            "json");//这里返回的类型有：json,html,xml,text
    },

    get_current_query:function () {
        var rtnCmd = "/api/vote/?Command=Query_Factory&pageindex={0}&pagesize={1}&fliter={2}";

        rtnCmd = $.StringFormat(rtnCmd, currentPageIndex.toString(),currentPageSize.toString(),fliterString);

        return rtnCmd;
    },
    query_vote_data: function ()
    {
        queryLock = true;
        var cmdString = $.get_current_query();
        $.apply_permition(userCookie);
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
                    if (Datas.length <= 0 || Datas.length < currentPageSize)
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
                        var oneT = $("#pinPaiList").html();
                        if("undefined" == typeof oneT)
                        {
                            oneT = "";
                        }

                        var abcTemp = {
                            fact_display1:"visible",
                            fact_logo1:"/static/factory/" + oneCode1.logoname + ".jpg",
                            fact_name1:oneCode1.name,
                            fact_vote_count1:oneCode1.voteCount,
                            fact_code1:oneCode1.code,
                        }

                        if (oneCode2 != null)
                        {
                            abcTemp["fact_display2"] = "visible";
                            abcTemp["fact_logo2"] = "/static/factory/" + oneCode2.logoname + ".jpg";
                            abcTemp["fact_name2"] = oneCode2.name;
                            abcTemp["fact_vote_count2"] = oneCode2.voteCount;
                            abcTemp["fact_code2"] = oneCode2.code;

                        }
                        else
                        {
                            abcTemp["fact_display2"] = "hidden";
                        }
                        // abcTemp.push({"vote_icon":"/static/Images/vote_1.png"});
                        if (isEnable == 0)
                        {
                            abcTemp["vote_icon"] = "/static/Images/vote_0.png";
                        }
                        else
                        {
                            abcTemp["vote_icon"] = "/static/Images/vote_1.png";
                        }

                        $("#pinPaiList").html(oneT + $.format(templateTemp,abcTemp) );


                        //
                        // $(document).on('click', "#" + oneCode2.code , function(){
                        //     alert( "aaaaafafew" );
                        // });
                        //
                        // $("#" + oneCode1.code).on('click', function(){
                        //     alert( "dfdsfs" );
                        // });
                    }
                    queryLock = false;
                }

            },
            "json");//这里返回的类型有：json,html,xml,text

    //    $("#click_div").on("click","img",function(){
    //     // $(this).css("border","5px solid #000");
    //     alert("afdsfs");
    // });
    },

    validCookie:function ()
        {
            userCookie = $.cookie('UserKey');
            lastDate = $.cookie('LastDate');

            // alert(ckValue);
            if (userCookie == "undefined" || userCookie == "" || userCookie == null)
            {
                userCookie = $.randomString(8);
                $.cookie("UserKey",userCookie);
            }

            if (lastDate == "undefined" || lastDate == "" || lastDate == null)
            {
                lastDate = $.getNowFormatDate();
                $.cookie("LastDate",lastDate);
            }
        },

    getNowFormatDate:function () {
        var date = new Date();
        var seperator1 = "-";
        var seperator2 = ":";
        var month = date.getMonth() + 1;
        var strDate = date.getDate();
        if (month >= 1 && month <= 9) {
            month = "0" + month;
        }
        if (strDate >= 0 && strDate <= 9) {
            strDate = "0" + strDate;
        }
        var currentdate = date.getFullYear() + seperator1 + month + seperator1 + strDate;
        return currentdate;
    },

    randomString:function(len) {
        len = len || 32;
        var $chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678';    /****默认去掉了容易混淆的字符oOLl,9gq,Vv,Uu,I1****/
        var maxPos = $chars.length;
        var pwd = '';
        for (i = 0; i < len; i++) {
            pwd += $chars.charAt(Math.floor(Math.random() * maxPos));
        }
        return pwd;
    },
    isNull:function (datas) {
            return (data == "" || data == undefined || data == null) ? 0 : 1;
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

    vote_mydata:function (fcode) {
        if (isEnable == 0)
        {
            alert("您今天已经投过票了!");
            return;
        }
        var rtnCmd = "/api/vote/?Command=VOTE_VOTING";

        $.post(rtnCmd, {ucode: userCookie, fcode: fcode},
            function (data)
            {

                var  ErrorId = data.ErrorId;
                var  Result = data.Result;

                if (ErrorId == 200)
                {
                    isEnable= 0;
                    eval("$(\"#" + fcode + "\").html('得票数：" + Result + "')");

                    alert("感谢参与!");
                }


            },
            "json");//这里返回的类型有：json,html,xml,text


    },
});