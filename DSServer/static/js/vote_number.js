/**
 * Created by jiaju_cao on 2017/6/7.
 */

window.onload=function()
{
    //$.load_voteResult();
};


// 自定义函数
$.extend({
    get_current_query:function () {
        var rtnCmd = "/api/vote/?Command=Query_Factory&pageindex={0}&pagesize={1}&fliter={2}&sort=1";

        rtnCmd = $.StringFormat(rtnCmd, 0,"10","");

        return rtnCmd;
    },
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

    vote_mydata:function (fcode) {
        if (isEnable == 0)
        {
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
                    isEnable = 0;
                    eval("$(\"#" + fcode + "\").html('得票数：" + Result + "')");

                    alert("感谢参与!");
                }


            },
            "json");//这里返回的类型有：json,html,xml,text


    },
});