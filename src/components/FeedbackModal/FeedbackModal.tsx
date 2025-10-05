import React from 'react';
import { MessageSquare, Star } from 'lucide-react';
import { Modal } from '@/components/ui/Modal';
import { FormGroup } from '@/components/ui/FormGroup';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Feedback } from '@/types';
import './FeedbackModal.css';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  feedback: Feedback;
  setFeedback: (feedback: Feedback) => void;
  onSubmit: () => void;
}

export const FeedbackModal: React.FC<FeedbackModalProps> = ({
  isOpen,
  onClose,
  feedback,
  setFeedback,
  onSubmit
}) => {
  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFeedback({ ...feedback, email: e.target.value });
  };

  const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setFeedback({ ...feedback, message: e.target.value });
  };

  const handleRatingChange = (rating: number) => {
    setFeedback({ ...feedback, rating });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Share Your Feedback"
      icon={<MessageSquare size={24} />}
    >
      <FormGroup label="Email">
        <Input
          type="email"
          placeholder="your@email.com"
          value={feedback.email}
          onChange={handleEmailChange}
        />
      </FormGroup>

      <FormGroup label="Rating">
        <div className="rating-selector">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              className={`star-button ${star <= feedback.rating ? 'active' : ''}`}
              onClick={() => handleRatingChange(star)}
            >
              <Star size={20} fill={star <= feedback.rating ? 'currentColor' : 'none'} />
            </button>
          ))}
        </div>
      </FormGroup>

      <FormGroup label="Message">
        <textarea
          placeholder="Tell us about your experience..."
          value={feedback.message}
          onChange={handleMessageChange}
          rows={4}
          className="feedback-textarea"
        />
      </FormGroup>

      <Button variant="modal-primary" onClick={onSubmit}>
        Submit Feedback
      </Button>
    </Modal>
  );
};
