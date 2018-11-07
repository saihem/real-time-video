// function pollResponses() {
//     setInterval(function()
//     {
//         $.ajax({
//             type: "get",
//             url: "/api/resps",
//             success:function(data) {
//                 if (!jQuery.isEmptyObject(data)) {
//                     $(".feeds").html('<tr class="placeholder"><td colspan="3"></td></tr>');
//                     for (let i = 0; i < data.length; i++) {
//                         $('.feed > .feeds').append('<tr><td>' + data[i].type + '</td><td>' + data[i].time + '</td><td>' + data[i].response + '</td></tr>');
//                     }
//                 }
//             }
//         });
//     }, 10000);//10000 milliseconds = 20 seconds
// };

//pollResponses();


$(document).ready(function() {
    $('#train').click(function () {
        $(".well").html('Sit Tight, images are being trained. 🧙');
        $.ajax({
                type: "get",
                url: "/api/train",
                success:function(data)
                {
                    console.log(data);
                    if(data[1]) {
                        $(".well").html("Images are Trained. Click Analyze! 🧙");
                    }else{
                        $(".well").html("Oops! We didn't recognize any name tags. Please TRAIN again with a name tag");
                    }

                }
            });
    });

    $('#analyze').click(function() {
        $(".well").html('Stick Tight, images are being analyzed. 🔮');
        $.ajax({
                type: "get",
                url: "/api/analyze",
                success:function(data)
                {
                    console.log(data);
                    if(data[1]) {
                        $(".well").html('Check the result below! 🔮');
                        $(".magic").html('<img src="https://media.giphy.com/media/12NUbkX6p4xOO4/giphy.gif">');
                    }else{
                        $(".well").html("Oops! We didn't recognize any faces. Please TRAIN again with a name tag");
                    }
                     $.ajax({
                        type: "get",
                        url: "/api/resps",
                        success: function(data) {
                        if (!jQuery.isEmptyObject(data)){
                            $(".feeds").html('<tr class="placeholder"><td colspan="3"></td></tr>');
                            for (let i = 0; i < data.length; i++) {
                                $('.feed > .feeds').append('<tr><td>' + data[i].type + '</td><td>' + data[i].time + '</td><td>' + data[i].response + '</td></tr>');
                            }
                            }
                        }
                     });

                }
            });
    });
});