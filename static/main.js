
(function($) {
	"use strict";

	$(".history-scroller").niceScroll({
		cursorwidth: "10px",
		background: "#0d1015",
		cursorborder: "0",
		cursorborderradius: "0",
		autohidemode: false,
		zindex: 5
	});

	$(".testimonials").owlCarousel({
		margin: 30,
		autoPlay: true,
		autoPlay : 5000,
		responsive: {
			0: {
				items: 1
			},
			480: {
				items: 1
			},
			768: {
				items: 1
			},
			1024: {
				items: 2
			}
		}
	});
	
	animatedProgressBar();
	windowHieght();
	contactFormValidation();
	previewPannel();

	function animatedProgressBar () {
		$(".progress").each(function() {
			var skillValue = $(this).find(".skill-lavel").attr("data-skill-value");
			$(this).find(".bar").animate({
				width: skillValue
			}, 1500, "easeInOutExpo");

			$(this).find(".skill-lavel").text(skillValue);
		});
	}

	function windowHieght(){
		if ( $(window).height() <=768 ) {
			$(".pt-table").addClass("desktop-768");
		} else {
			$(".pt-table").removeClass("desktop-768");
		}
	}
	
	/*----------------------------------------
		contact form validation
	------------------------------------------*/
	function contactFormValidation() {
		$(".contact-form").validate({
		    rules: {
		        name: {
		            required: true
		        },
		        email: {
		            required: true,
		            email: true
		        },
		        subject: {
		            required: true
		        },
		        message: {
		            required: true
		        }
		    },
		    messages: {
		        name: {
		            required: "Write your name here"
		        },
		        email: {
		            required: "No email, no support"
		        },
		        subject: {
		            required: "you have a reason to contact, write it here"
		        },
		        message: {
		            required: "You have to write something to send this form"
		        }
		    },
		    submitHandler: function(form) {
		        // $(form).ajaxSubmit({
		            // type: "POST",
		            // data: $(form).serialize(),
		            // url : 'mail.php',
		            // success: function() {
						form.submit();
						// $('/donate_success');
		                // $(".contact-form").fadeTo( "slow", 1, function() {
		                //     $(".contact-form .msg-success").slideDown();
		                // });
		                // $(".contact-form").resetForm();	
		            // },
		            // error: function() {
		            //     $(".contact-form").fadeTo( "slow", 1, function() {
		            //         $(".contact-form .msg-failed").slideDown();
		            //     });
		            // }
		        // });
		    },
		    errorPlacement: function(error, element) {
		        element.after(error);
		        error.hide().slideDown();
		    }
		}); 
	}

	/*----------------------------------------
		Isotope Masonry
	------------------------------------------*/
	function isotopeMasonry() {
		$(".isotope-gutter").isotope({
		    itemSelector: '[class^="col-"]',
		    percentPosition: true
		});
		$(".isotope-no-gutter").isotope({
		    itemSelector: '[class^="col-"]',
		    percentPosition: true,
		    masonry: {
		        columnWidth: 1
		    }
		});

		$(".filter a").on("click", function(){
		    $(".filter a").removeClass("active");
		    $(this).addClass("active");
		   // portfolio fiter
		    var selector = $(this).attr("data-filter");
		    $(".isotope-gutter").isotope({
		        filter: selector,
		        animationOptions: {
		            duration: 750,
		            easing: "linear",
		            queue: false
		        }
		    });
		    return false;
		});
	}

	/*=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
	    Preview Pannel
	-=-=-=-=-=-=-=-=-=--=-=-=-=-=-*/
	function previewPannel() {
	    $(".switcher-trigger").on("click", function() {
	        $(".preview-wrapper").toggleClass("extend");
	        return false;
	    });
	    if ($(window).width() < 768 ) {            
	        //$(".preview-wrapper").removeClass("extend");            
	    }
	    $(".color-options li").on("click", function(){
	        if ($("body").hasClass("back-step")) {
	            $("#color-changer").attr({
	                "href":"../css/colors/"+$(this).attr("data-color")+".css"
	            });
	        }else {
	            $("#color-changer").attr({
	                "href":"css/colors/"+$(this).attr("data-color")+".css"
	            });
	        }
	        return false;
	    });
	}
	
	$(window).on("load", function() {
		$(".preloader").addClass("active");
		isotopeMasonry();
		setTimeout(function () {
		    $(".preloader").addClass("done");
		}, 1500);
	});
})(jQuery);

var subjectObject = {
	"Coimbatore": {
	  "Coimbatore North": ["Ganapathy", "Rathinapuri", "P.N.Pudhur", "Venkittapuram","Maniyakaranpalayam","Koilmedu","Nallampalyam","Sanganoor","Ramakrishnapuram","K.K.Pudhur","Gandhi Managar","Maruthamalai","Vadavalli","Ramasamy Nagar","S.B.Colony"],
	  "Coimbatore South": ["Town Hall","ukkadam","Puliyakulam", "Maruthur","Anupparpalayam","Ranganathapuram","Ramnagar","Gandhipuram","Sidhapudhur","Pappanaickenpalayam","Tatabad","Ramalingam Colony","Kamarajapuram","Okkiliar Colony","Selvapuram","Sukrawarpet"],
	  "Singanallur": ["Singanallur","Ondipudhur","Peelamedu","Avarampalayam","Krishnarayapuram","Lakshmi Mills Colony","Balaranganathapuram","Sowripalayam","Udayampalayam","Masakalipalayam","Pappanaickenpalayam","Uppilipalayam","Varadharajapuram","Krishnapuram","Neelikonampalayam","S.I.H.S. Colony","KPR Layout","Kallimadai","Saramedu","Ramanathapuram","Nanjundapuram","Abirami Nagar"],
	  "Kavundampalayam": ["Kavundampalayam","Edayarpalayam","Kovilpalayam","Kurumbapalayam","Keeranatham","Vattamalaipalayam","Vellakinar","Chinnavedampatti","Saravanampatti","Vilankurichi","Cheranmaanagar","Kalapatti","Kovanur","Naickenpalayam","Palamalai","Shajahan Nagar","Jothipuram","Kasthuripalayam","P.N.Palayam","Narasimhanaickenpalayam","Rakkipalayam","Kurudampalayam","Vadamadhurai","Asokapuram","Palanigoundenpudur","Thoppampatti","Kathirnaikenpalayam","Idikarai","Thudiyalur","Appanaickenpalayam","Subramaniyampalayam","Pannimadai","Kanuvaipalayam","Thaliyur","Nanjudapuram","Somayanur","Chinnathadagam","Veerapandi","Anaikatti","Thottipalayam","Samanaickenpalayam","A.S.Kulam","Athipalayam"],
	  "Thondamuthur": ["Thondamuthur","RS Puram","Selvapuram","Karumpukkadai","Ukkadam","Perur","Thelugupalayam","Kallamedu","Thondamuthur","Sugunapuram","Kuniyamuthur","Kovaipudur","Vedapatty","Sundakkamuthur","Thaliyur","Deenampalayam","Uliyampalayam","Kalikkanaickenpalayam","Kulathupalayam","Thennamanallur","Devarayapuram","Pullakavundenpudur","Mutthipalayam","Kembanur","Kaliyannanpudur","Narasipuram","Jagirnaickenpalayam","Vellimalaipattinam","Viraliyur","Boluvampatti","Semmedu","Iruttupallam","Seengapathy","Alandurai","Srinivasapuram","Karadimadai"],
	  "Kinathukadavu": ["Kinathukadavu","Podanur","Aathupalam","Ettimadai","Ganeshapuram","Malumichampatti","Madukkarai","Mathampatti","Kuppanoor","K.K.Chavadi","Kalampalayam","Theethipalayam","Chettipalayam","Vellalore","Eachanari","Sundarapuram","Kurichi","Machampalayam","Valukkal","Vazhukkuparai","Thoppampalayam"],
	  "Mettupalayum":["Mettupalayam","Karamadai","Nellithurai","Kallar","Odanthurai","Sirumugai","Thekkampatti","Gudalur","Oomapalayam","Palapatty","Vellipalayam","Karattumedu","Mothepalayam","Mulathurai","Eluppapalayam","Irumbarai","Sittepalayam","Chinnakallipatty","Kuttaiyur","Aayarpadi","Velliangadu"],
	  "sulur":["Sulur","Neelambur","Chinniyampalayam","Irugur","Somanur","Arasur","Sultanpet","Muthalipalayam","Kamatchipuram","Kurumbapalayam","Kalangal","Kadambadi","Pallapalayam","Selakarichal","Odderpalayam","Sellappampalayam","Kaniyur","Elachipalayam","Salaipudur"],
	  "Pollachi":["Pollachi","Puliampatti","Karacheri","Arasampalayam","Panappatti","Mandrampalayam","Vadachithur","Kondampatti","Mathegoundenpudur","Kattampatti","Chettiyakkapalayam","Thamaraikulam","Kalathur","Negamam","Devampadi","Senkuttaipalayam","Vellalapalayam","Achipatti","Vadugapalayam","Mahalingapuram","Kottampatti"],
	  "Valparai":["Valparai","Anaimalai","Kallar","Anaimudi","Pethanaickanur","Somandurai","Thensithur","Thensangamplayam","Navamalai","Ponkaliyur","Kottur","Palaniyur","Angalakuruchi","Kambalapatti","Paramadaiyur","Topslip","Sethumadai","Devipattinam","Vettaikaranpudur","Divansapudur","Authupollachi","Vakkampalayam","Odayakulam","Pachamalai"]
	},
	"Tiruppur": {
	  "Tiruppur North" :[],
	  "Tiruppur South":[],
	  "Udumalaipettai":[],
	  "Madathukulam":[],
	  "Palladam": [],
	  "Kangayam": [],
	  "Dharapuram":[],
	  "Avinashi":[],
	  
	}
  }
  
  window.onload = function() {
	var subjectSel = document.getElementById("subject");
	var topicSel = document.getElementById("topic");
	var chapterSel = document.getElementById("chapter");
	for (var x in subjectObject) {
	  subjectSel.options[subjectSel.options.length] = new Option(x, x);
	}
	subjectSel.onchange = function() {
	  //empty Chapters- and Topics- dropdowns
	  chapterSel.length = 1;
	  topicSel.length = 1;
	  //display correct values
	  for (var y in subjectObject[this.value]) {
		topicSel.options[topicSel.options.length] = new Option(y, y);
	  }
	}
	topicSel.onchange = function() {
	  //empty Chapters dropdown
	  chapterSel.length = 1;
	  //display correct values
	  var z = subjectObject[subjectSel.value][this.value];
	  for (var i = 0; i < z.length; i++) {
		chapterSel.options[chapterSel.options.length] = new Option(z[i], z[i]);
	  }
	}
  }
