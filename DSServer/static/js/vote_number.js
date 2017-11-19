/**
 * Created by jiaju_cao on 2017/6/7.
 */

var isFinishLoad = false;
var currentPageIndex = -1;
var currentPageSize = 10;
var queryLock = false;

var tempLate = "        <div class=\"pai_hang_back\">\n" +
    "            <img src=\"{number_img}\" style=\"width: 140px;height: 140px;float: left;margin-left: 50px;margin-top: 10px;border-radius:70px\">\n" +
    "            <div style=\"font-size: 1.7cm; color: #666666;float: left;margin-left: 40px;margin-top: 40px\">{number}</div>\n" +
    "            <div style=\"float: left;margin-left: 40px;font-size: 1.3cm;color: #707070;margin-top: 40px\">{number_name}</div>\n" +
    "            <div style=\"float: right;font-size: 0.8cm;color: crimson;margin-right: 40px;margin-top: 55px\">得票：{number_vote_count}</div>\n" +
    "        </div>"

window.onload=function()
{
    //$.load_voteResult();
};

$(document).ready(function()
{
    $(window).scroll(function(){
        var srollPos = $(window).scrollTop();
        var documentHd = $(document).height();
        var winHd = $(window).height() ;


        totalheight = parseFloat($(window).height()) + parseFloat(srollPos);

        if (srollPos + winHd > documentHd*0.85 && !isFinishLoad && !queryLock)
        {
            queryLock = true;
             // 加载数据
            currentPageIndex = currentPageIndex + 1;
            $.query_vote_number();
        }

        });

});


// 自定义函数
$.extend({
    load_voteResult: function ()
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

    get_query_cmd:function () {
        var rtnCmd = "/api/vote/?Command=Query_Vote_Number&pageindex={0}&pagesize={1}&start=5";

        rtnCmd = $.StringFormat(rtnCmd, currentPageIndex,currentPageSize);

        return rtnCmd;
    },
    query_vote_number:function (fcode) {
        var cmdString = $.get_query_cmd();
        // $.apply_permition(userCookie);
        // 提取用户名
        $.get( cmdString,
            function (data)
            {

                //alert(templateTemp);
                // 检查查询状态
                var  ErrorId = data.ErrorId;
                var  Result = data.Result;
                var Datas = Result
                if (ErrorId == 200)
                {
                    if (Datas.length <= 0 || Datas.length < currentPageSize)
                    {
                        isFinishLoad = true;
                    }

                    for (i=0;i<Datas.length ;i++ )
                    {
                        var oneCode1 = Datas[i];
                        var oneT = $("#pageContainer").html();
                        if("undefined" == typeof oneT)
                        {
                            oneT = "";
                        }

                        var abcTemp = {};
                        abcTemp["number_img"] = oneCode1.number_img;
                        abcTemp["number"] = oneCode1.number;
                        abcTemp["number_name"] = oneCode1.number_name;
                        abcTemp["number_vote_count"] = oneCode1.number_vote_count;

                        var oneT = $("#pageContainer").html();
                        $("#pageContainer").html(oneT + $.format(tempLate,abcTemp) );
                    }

                    queryLock = false;
                }

            },
            "json");//这里返回的类型有：json,html,xml,text
    },
});