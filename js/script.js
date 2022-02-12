imgInp = document.getElementById("imgID");
img = document.getElementById("user-img");
uploadBtn = document.getElementById("upload-btn");
imgInp.onchange = evt => {
  const [file] = imgInp.files
  if (file) {
    img.src = URL.createObjectURL(file)
    uploadBtn.hidden = true;
    const cropper = new Cropper(img, {
      crop(event) {

        document.getElementById("cropX").value = event.detail.x;
        document.getElementById("cropY").value = event.detail.y;
        document.getElementById("cropW").value = event.detail.width;
        document.getElementById("cropH").value = event.detail.height;

        console.log(event.detail.x);
        console.log(event.detail.y);
        console.log(event.detail.width);
        console.log(event.detail.height);
        console.log(event.detail.rotate);
        console.log(event.detail.scaleX);
        console.log(event.detail.scaleY);
      },
    });
  }
  uploadBtn.hidden = false;
}

