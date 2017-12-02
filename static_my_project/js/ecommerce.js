$(document).ready(function(){
    //Contact for handler
    var contactForm = $(".contact-form");
    var contactFormMethod = contactForm.attr("method");
    var contactFormEndpoint = contactForm.attr("action");
    var contactFormSubmitBtn = contactForm.find("[type='submit']");
     var contactFormSubmitBtnTxt=contactFormSubmitBtn.text();

     function displaySubmitting(doSubmit){
        if(doSubmit){
            contactFormSubmitBtn.addClass("disabled");
            contactFormSubmitBtn.html("<i class='fa fa-spin fa-spinner'></i>Sending...");
        }
        else{
            contactFormSubmitBtn.removeClass("disabled");
            contactFormSubmitBtn.html(contactFormSubmitBtnTxt);
        }
     }

      contactForm.submit(function(event){
        event.preventDefault();
         var contactFormData = contactForm.serialize();
         var thisForm = $(this);
         displaySubmitting(true);
         $.ajax({
            url: contactFormEndpoint,
             method: contactFormMethod,
             data: contactFormData,
              success: function(data){
                  thisForm[0].reset();
                  setTimeout(function(){
                    $.alert({
                        title: "Success!",
                        content: data.message,
                        theme: "modern",
                    });
                    displaySubmitting(false);
                  }, 2000);
              },
               error: function(errorData){
                    var jsonData=errorData.responseJSON;
                    var msg ="";

                     $.each(jsonData, function(key, value){
                        msg += key + ": " + value[0].message + "\n";
                     })

                     $.alert({
                        title: "Oops",
                        content: msg,
                        theme: "modern",
                     });
                     displaySubmitting(false);
                }
         })
      })


    //Auto Search
    var searchForm = $(".search-form");
    var searchInput = searchForm.find("[name='q']");
    var typingTimer;
    var typingInterval = 1000 //.5 sec
    var searchBtn = searchForm.find("[type='submit']");

    searchInput.keyup(function(event){
        clearTimeout(typingTimer);
        typingTimer = setTimeout(performSearch, typingInterval);
    });

    searchInput.keydown(function(event){
        clearTimeout(typingTimer);
    });

    function displaySearch(){
        searchBtn.addClass("disabled");
        searchBtn.html("<i class='fa fa-spin fa-spinner'></i> Searching...");
    }

    function performSearch(){
        displaySearch();
        var query = searchInput.val();
        setTimeout(function(){
            window.location.href='/search/\?q=' + query;
        }, 1000)
    }


    //Cart and Add products
    var productForm = $('.form-product-ajax');
    productForm.submit(function(event){
        event.preventDefault();
        var thisForm = $(this);
        var actionEndpoint = thisForm.attr("data-endpoint");
        var httpMethod = thisForm.attr("method");
        var formData = thisForm.serialize();

        $.ajax({
            url: actionEndpoint,
            method: httpMethod,
            data: formData,
            success: function(data){
                var submitSpan = thisForm.find(".submit-span");
                var navbarCount = $('.navbar-cart-count');

                if(data.added){
                    submitSpan.html('In cart <button type="submit" class="btn btn-link">Remove?</button>')
                }
                else{
                    submitSpan.html('<button type="submit" class="btn btn-success">Add to cart</button>')
                }
                navbarCount.text(data.cartItemCount);
                if(window.location.href.indexOf("cart") != -1){
                    refreshCart();
                }
            },
            error: function(errorData){
                $.alert({
                title: "Oops",
                content: "An error occurred",
                theme: "modern"});
            }
        })
    })

    function refreshCart(){
        var cartTable = $(".cart-table");
        var cartBody = cartTable.find(".cart-body");
        var productRows = cartBody.find(".cart-products");
        var currentUrl = window.location.href

        var refreshCartUrl = '/api/cart/'
        var refreshCartMethod = "GET";
        var data = {};
        $.ajax({
            url: refreshCartUrl,
            method: refreshCartMethod,
            data: data,
            success: function(data){

                var hiddenCartItemRemoveForm=$(".cart-item-remove-form");
                if(data.products.length > 0){
                    productRows.html("");
                    cartBody.find(".cart-subtotal").text(data.subtotal);
                    cartBody.find(".cart-total").text(data.total);
                    var i=1;
                    $.each(data.products, function(index, value){
                        var newCartItemRemove = hiddenCartItemRemoveForm.clone();
                        newCartItemRemove.css("display", "block");
                        newCartItemRemove.find(".cart-item-product-id").val(value.id);
                        cartBody.prepend("<tr><th scope='row'>" + i +"</th><td><a href='"+ value.url +"'>" + value.name +"</a>" + newCartItemRemove.html() + "</td><td>"+ value.price +"</td></tr>");
                        i--;
                    })

                }
                else{
                    window.location.href = currentUrl;
                }
            },
            error: function(errorData){
                $.alert({
                title: "Oops",
                content: "An error occurred",
                theme: "modern"});
            }
        })
    }
    });