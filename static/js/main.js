function pollResponses() {
    setInterval(function()
    {
        $.ajax({
            type: "get",
            url: "/api/resps",
            success:function(data)
            {
                console.log(data);
                $('.feed > .feeds > tr:first').before('<tr><td>'+data.type+'</td><td>'+data.time+'</td><td>'+data.response+'</td></tr>');
            }
        });
    }, 10000);//10000 milliseconds = 20 seconds
};


pollResponses();