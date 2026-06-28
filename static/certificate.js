// Certificate generation and download functionality
// Handles PDF generation for completed learning paths

(function() {
  'use strict';

  /**
   * Generate a downloadable PDF certificate for a completed learning path.
   * Requires jsPDF library to be included in the page.
   */
  function generateCertificatePDF(certificateData) {
    if (typeof jsPDF === 'undefined') {
      console.error('jsPDF library not loaded. Cannot generate certificate.');
      return false;
    }

    try {
      var doc = new jsPDF({
        orientation: 'landscape',
        unit: 'mm',
        format: 'a4'
      });

      // Set up document properties
      doc.setProperties({
        title: 'DevPath Completion Certificate',
        subject: 'Course Completion Certificate',
        author: 'DevPath'
      });

      // Border
      doc.setDrawColor(100, 150, 200);
      doc.setLineWidth(2);
      doc.rect(15, 15, 270, 200);

      // Decorative inner border
      doc.setDrawColor(150, 180, 220);
      doc.setLineWidth(0.5);
      doc.rect(20, 20, 260, 190);

      // Title
      doc.setFontSize(36);
      doc.setTextColor(40, 80, 140);
      doc.setFont('helvetica', 'bold');
      doc.text('Certificate of Completion', 148, 60, { align: 'center' });

      // Subtitle
      doc.setFontSize(14);
      doc.setTextColor(60, 60, 60);
      doc.setFont('helvetica', 'normal');
      doc.text('This certifies that', 148, 90, { align: 'center' });

      // Learner name
      doc.setFontSize(24);
      doc.setTextColor(40, 80, 140);
      doc.setFont('helvetica', 'bold');
      doc.text(certificateData.learner_name, 148, 110, { align: 'center' });

      // Completion text
      doc.setFontSize(14);
      doc.setTextColor(60, 60, 60);
      doc.setFont('helvetica', 'normal');
      doc.text('has successfully completed', 148, 130, { align: 'center' });

      // Path name
      doc.setFontSize(20);
      doc.setTextColor(40, 80, 140);
      doc.setFont('helvetica', 'bold');
      doc.text(certificateData.path_name, 148, 150, { align: 'center' });

      // Completion date
      doc.setFontSize(12);
      doc.setTextColor(60, 60, 60);
      doc.setFont('helvetica', 'normal');
      var dateText = 'Completed on ' + certificateData.completion_date;
      doc.text(dateText, 148, 170, { align: 'center' });

      // Verification code
      doc.setFontSize(10);
      doc.setTextColor(100, 100, 100);
      doc.setFont('helvetica', 'italic');
      var verificationText = 'Verification Code: ' + certificateData.verification_code;
      doc.text(verificationText, 148, 185, { align: 'center' });

      // DevPath branding
      doc.setFontSize(11);
      doc.setTextColor(100, 150, 200);
      doc.setFont('helvetica', 'bold');
      doc.text('DevPath', 30, 195);

      var fileName = 'devpath-certificate-' + certificateData.path_id + '.pdf';
      doc.save(fileName);

      return true;
    } catch (error) {
      console.error('Error generating certificate PDF:', error);
      return false;
    }
  }

  /**
   * Handle certificate download button click.
   */
  function handleCertificateDownload(event) {
    event.preventDefault();

    var pathId = event.target.getAttribute('data-path-id');
    var learnerName = event.target.getAttribute('data-learner-name');
    var pathName = event.target.getAttribute('data-path-name');
    var completionDate = event.target.getAttribute('data-completion-date');
    var verificationCode = event.target.getAttribute('data-verification-code');

    if (!pathId || !learnerName || !pathName) {
      console.error('Missing required certificate data');
      return false;
    }

    var certificateData = {
      path_id: pathId,
      learner_name: learnerName,
      path_name: pathName,
      completion_date: completionDate,
      verification_code: verificationCode
    };

    var success = generateCertificatePDF(certificateData);

    if (success) {
      console.log('Certificate downloaded successfully');
    } else {
      alert('Failed to generate certificate. Please try again.');
    }

    return false;
  }

  /**
   * Attach click handlers to all certificate download buttons.
   */
  function initializeCertificateButtons() {
    var buttons = document.querySelectorAll('.btn-download-certificate');
    buttons.forEach(function(button) {
      button.addEventListener('click', handleCertificateDownload);
    });
  }

  // Initialize on page load
  document.addEventListener('DOMContentLoaded', initializeCertificateButtons);

  // Export for testing
  window.CertificateGenerator = {
    generateCertificatePDF: generateCertificatePDF,
    handleCertificateDownload: handleCertificateDownload,
    initializeCertificateButtons: initializeCertificateButtons
  };
})();
