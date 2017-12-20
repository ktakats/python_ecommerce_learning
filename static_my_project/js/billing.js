$(document).ready(function(){
    var stripeFormModule = $(".stripe-payment-form");
    var stripeModuleToken = stripeFormModule.attr("data-token");
    var stripeModuleNextUrl = stripeFormModule.attr("data-next-url");
    var stripeModuleBtnTitle = stripeFormModule.attr("data-btn-title") || "Add card";

    var stripeTemplate = $.templates("#stripeTemplate");
    var stripeTemplateDataContext = {
        name: "Stripe",
        publishKey: stripeModuleToken,
        nextUrl: stripeModuleNextUrl,
        btnTitle: stripeModuleBtnTitle
    };
    var stripeTemplateHtml = stripeTemplate.render(stripeTemplateDataContext);
    stripeFormModule.html(stripeTemplateHtml);

    var paymentForm = $(".payment-form");

    if (paymentForm.length > 1){
        alert("Only one payment form is allowed per page");
        paymentForm.css('display', 'none');
    }
    else if (paymentForm.length == 1){
        var pubKey = paymentForm.attr('data-token');
        var nextUrl = paymentForm.attr('data-next-url');
    }

    // Create a Stripe client
    var stripe = Stripe(pubKey);

    // Create an instance of Elements
    var elements = stripe.elements();

    // Custom styling can be passed to options when creating an Element.
    // (Note that this demo uses a wider set of styles than the guide below.)
    var style = {
      base: {
        color: '#32325d',
        lineHeight: '18px',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
          color: '#aab7c4'
        }
      },
      invalid: {
        color: '#fa755a',
        iconColor: '#fa755a'
      }
    };

    // Create an instance of the card Element
    var card = elements.create('card', {style: style});

    // Add an instance of the card Element into the `card-element` <div>
    card.mount('#card-element');

    // Handle real-time validation errors from the card Element.
    card.addEventListener('change', function(event) {
      var displayError = document.getElementById('card-errors');
      if (event.error) {
        displayError.textContent = event.error.message;
      } else {
        displayError.textContent = '';
      }
    });

    // Handle form submission
    var form = document.getElementById('payment-form');
    form.addEventListener('submit', function(event) {
      event.preventDefault();

      stripe.createToken(card).then(function(result) {
        if (result.error) {
          // Inform the user if there was an error
          var errorElement = document.getElementById('card-errors');
          errorElement.textContent = result.error.message;
        } else {
          // Send the token to your server
          stripeTokenHandler(nextUrl, result.token);
        }
      });
    });

    function redirectToNext(nextPath){
        if (nextPath){
            setTimeout(function(){
                window.location.href=nextUrl;
            }, 1500);
        }
    }

    function stripeTokenHandler(nextUrl, token){
        var paymentMethodEndpoint = '/billing/payment-method/create/';
        var data = {"token": token.id};

        $.ajax({
            data: data,
            url: paymentMethodEndpoint,
            method: "POST",
            success: function(result){
                var successMsg = result.message || "Success";
                console.log(result)
                card.clear();
                if ($.alert){
                    $.alert(successMsg);
                }
                else {
                    alert(successMsg);
                }
                redirectToNext(nextUrl);
            },
            error: function(error){}
        });
    }
});